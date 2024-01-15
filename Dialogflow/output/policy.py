# File generated automatically on 2024-01-15 20:07 by instrumenter.py
#  - Agent: AssistantAgent
#  - Input zip: Examples/Factory/AssistantAgentFR.zip
#  - Output zip: output/AssistantAgentMonitored.zip
#  - WebHook URL: https://fff7-79-30-45-250.ngrok-free.app
#  - Monitor URL: http://localhost:8081
#  - Monitoring Level: 2


# IMPORTS
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, requests, random

class WebHookResponder(BaseHTTPRequestHandler):

	# The url on which the monitor is listening
	MONITOR_URL = "http://localhost:8081"

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
			self.add_object()
		if message["queryResult"]["intent"]["displayName"] == "AddRelObject":
			self.add_rel_object()

		# If the intent needs a webhook answer the request is performed
		if message["queryResult"]["intent"]["displayName"] in ["AddObject", "RemoveObject", "AddRelObject"]:
			self.wfile.write(bytes(requests.post("https://localhost:8082", message)))

	def add_object(self):
		available_answers = ['No answer from the server.']
		message = "{\"fulfillmentMessages\": [{\"text\": [\"" + random.choice(available_answers)+ "\"]}]}"
		oracle_message = {}
		oracle_message["sender"] = "bot"
		oracle_message["receiver"] = "user"
		oracle_message["bot_action"] = "add_object"
		oracle_message = json.dumps(oracle_message)
		if not self.question_oracle(oracle_message):
			return
		self.wfile.write(bytes(message, 'utf8')) 

	def add_rel_object(self):
		available_answers = ['No answer from the server.']
		message = "{\"fulfillmentMessages\": [{\"text\": [\"" + random.choice(available_answers)+ "\"]}]}"
		oracle_message = {}
		oracle_message["sender"] = "bot"
		oracle_message["receiver"] = "user"
		oracle_message["bot_action"] = "add_rel_object"
		oracle_message = json.dumps(oracle_message)
		if not self.question_oracle(oracle_message):
			return
		self.wfile.write(bytes(message, 'utf8')) 



def run(PORT):
	print("Server launch...")
	httpd = HTTPServer(("", PORT), WebHookResponder)
	httpd.serve_forever()

run(8080)
