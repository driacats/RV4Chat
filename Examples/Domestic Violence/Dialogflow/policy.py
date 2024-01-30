# File generated automatically on 2024-01-30 15:44 by instrumenter.py
#  - Agent: DomesticViolenceHelper
#  - Input zip: ../Examples/Domestic Violence/Dialogflow/DomesticViolenceHelper.zip
#  - Output zip: output/DomesticViolenceHelperMonitored.zip
#  - WebHook URL: https://163e-130-251-61-251.ngrok-free.app
#  - Monitor URL: ws://localhost:5052
#  - Monitoring Level: 2


# IMPORTS
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, requests, random, urllib3
from websocket import create_connection

class WebHookResponder(BaseHTTPRequestHandler):

	# The url on which the monitor is listening
	MONITOR_URL = "ws://localhost:5052"
	ws = create_connection(MONITOR_URL)
	http = urllib3.PoolManager()

	# The function simply sends an error message back to Dialogflow
	def send_error_message(self):
		message = "{\"fulfillmentMessages\":[{\"text\":{\"text\":[\"Error thrwon from the monitor!\"]}}]}"
		self.wfile.write(bytes(message, 'utf8'))

	# The function builds a message following the monitor protocol:
	# 	- sender		[bot|user]
	#	- receiver		[user|bot]
	#	- intent
	#	- entities
	def msg2json(self, message):
		json_obj = {}
		json_obj["sender"] = "user"
		json_obj["receiver"] = "bot"
		intent = {}
		intent["name"] = message["queryResult"]["intent"]["displayName"]
		intent["confidence"] = message["queryResult"]["intentDetectionConfidence"]
		json_obj["intent"] = intent
		entities = {}
		for param in message["queryResult"]["parameters"]:
			entities[param.lower()] = message["queryResult"]["parameters"][param]
		json_obj["entities"] = entities
		return json.dumps(json_obj)

	def question_oracle(self, event_str):
		# // ws = create_connection(self.MONITOR_URL)
		# We send it to the monitor and wait for the answer.
		self.ws.send(event_str)
		oracle = json.loads(self.ws.recv())
		# self.ws.close()
		print("[EVENT]", event_str)
		print("[ORACLE]", oracle)
		if not oracle["verdict"]:
			self.send_error_message()
			return False
		return True

	def do_POST(self):
		# Accept the request
		content_length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(content_length)
		message = json.loads(post_data)
		user_event = self.msg2json(message)

		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		# Send the user input event to the monitor
		if not self.question_oracle(user_event):
			print("[LOG] Monitor Error.")
			return
		if message["queryResult"]["intent"]["displayName"] == "Default Welcome Intent":
			self.input_welcome()
		if message["queryResult"]["intent"]["displayName"] == "Default Fallback Intent":
			self.input_unknown()

		# If the intent needs a webhook answer the request is performed
		if message["queryResult"]["intent"]["displayName"] in ["inform_chatbot_about_salary", "commit_suicide", "inform_chatbot_about_children", "undo_word", "get_information", "help_word"]:
			webhook_answer = requests.post("http://localhost:8082", json=message)
			webhook_answer = self.http.request('POST', "http://localhost:8082", body=json.dumps(message))
			webhook_answer = json.loads(webhook_answer.data)
			webhook_answer["sender"] = "bot"
			webhook_answer["receiver"] = "user"
			if not self.question_oracle(json.dumps(webhook_answer)):
				print("[LOG] Monitor error")
				return
			self.wfile.write(bytes(json.dumps(webhook_answer), 'utf8'))

	def input_welcome(self):
		available_answers = ['Hi! How are you doing?', 'Hello! How can I help you?', 'Good day! What can I do for you today?', 'Greetings! How can I assist?']
		message = "{\"fulfillmentMessages\": [{\"text\": [\"" + random.choice(available_answers)+ "\"]}]}"
		oracle_message = {}
		oracle_message["sender"] = "bot"
		oracle_message["receiver"] = "user"
		oracle_message["bot_action"] = "input_welcome"
		oracle_message = json.dumps(oracle_message)
		if not self.question_oracle(oracle_message):
			return
		self.wfile.write(bytes(message, 'utf8')) 

	def input_unknown(self):
		available_answers = ["I didn't get that. Can you say it again?", 'I missed what you said. What was that?', 'Sorry, could you say that again?', 'Sorry, can you say that again?', 'Can you say that again?', "Sorry, I didn't get that. Can you rephrase?", 'Sorry, what was that?', 'One more time?', 'What was that?', 'Say that one more time?', "I didn't get that. Can you repeat?", 'I missed that, say that again?']
		message = "{\"fulfillmentMessages\": [{\"text\": [\"" + random.choice(available_answers)+ "\"]}]}"
		oracle_message = {}
		oracle_message["sender"] = "bot"
		oracle_message["receiver"] = "user"
		oracle_message["bot_action"] = "input_unknown"
		oracle_message = json.dumps(oracle_message)
		if not self.question_oracle(oracle_message):
			return
		self.wfile.write(bytes(message, 'utf8')) 



def run(PORT):
	print("Server launch...")
	httpd = HTTPServer(("", PORT), WebHookResponder)
	httpd.serve_forever()

run(8080)
