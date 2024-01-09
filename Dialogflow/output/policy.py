# File generated automatically on 2024-01-09 17:43 by instrumenter.py
#  - Agent: AgentsInFactory
#  - Input zip: Examples/AgentsInFactory.zip
#  - Output zip: output/prova.zip
#  - WebHook URL: https://78a3-130-251-61-251.ngrok-free.app
#  - Monitor URL: http://127.0.0.1:5052
#  - Monitoring Level: 2


# IMPORTS
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, requests, random

class WebHookResponder(BaseHTTPRequestHandler):

	# The url on which the monitor is listening
	MONITOR_URL = "http://127.0.0.1:5052"

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
			entities[param] = message["queryResult"]["parameters"][param]
		json_obj["entities"] = entities
		return json.dumps(json_obj)

	def question_oracle(self, event_str):
		ws = create_connection("ws://localhost:5052")
		# We send it to the monitor and wait for the answer.
		ws.send(event_str)
		oracle = json.loads(ws.recv())
		ws.close()
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
			return
		if message["queryResult"]["intent"]["displayName"] == "AddObject":
			self.()
		if message["queryResult"]["intent"]["displayName"] == "Default Welcome Intent":
			self.input_welcome()
		if message["queryResult"]["intent"]["displayName"] == "Default Fallback Intent":
			self.input_unknown()
		if message["queryResult"]["intent"]["displayName"] == "Try Response":
			self.()

		# If the intent needs a webhook answer the request is performed
		if message["queryResult"]["intent"]["displayName"] in ["RemoveObject", "Exit", "AddObject", "Call Jason Agent"]:
			self.wfile.write(bytes(requests.post("https://37c4-130-251-216-39.eu.ngrok.io", message)))

	def (self):
		available_answers = ['The DialogFlow Agent here! How can I help you?']
		message = "{\"fulfillmentMessages\": [{\"text\": [\"" + random.choice(available_answers)+ "\"]}]}"
		oracle_message = {}
		oracle_message["sender"] = "bot"
		oracle_message["receiver"] = "user"
		oracle_message["bot_action"] = ""
		oracle_message = json.dumps(oracle_message)
		if not self.question_oracle(oracle_message):
			return
		self.wfile.write(bytes(message, 'utf8')) 

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

	def (self):
		available_answers = ['The DialogFlow Agent here! How can I help you?']
		message = "{\"fulfillmentMessages\": [{\"text\": [\"" + random.choice(available_answers)+ "\"]}]}"
		oracle_message = {}
		oracle_message["sender"] = "bot"
		oracle_message["receiver"] = "user"
		oracle_message["bot_action"] = ""
		oracle_message = json.dumps(oracle_message)
		if not self.question_oracle(oracle_message):
			return
		self.wfile.write(bytes(message, 'utf8')) 



def run(PORT):
	print("Server launch...")
	httpd = HTTPServer(("", PORT), WebHookResponder)
	httpd.serve_forever()

run(8080)
