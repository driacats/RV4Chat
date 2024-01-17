# IMPORTS
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, requests, random
from websocket import create_connection

class WebHookResponder(BaseHTTPRequestHandler):

	# The url on which the monitor is listening
	MONITOR_URL = MONITOR_URL_PLACEHOLDER

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
		ws = create_connection(self.MONITOR_URL)
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
CALL_ANSWER_FUNCTIONS_PLACEHOLDER
		# If the intent needs a webhook answer the request is performed
		if message["queryResult"]["intent"]["displayName"] in INTENT_LIST_PLACEHOLDER:
			webhook_answer = requests.post(YOUR_URL_PLACEHOLDER, json=message)
			webhook_answer = json.loads(webhook_answer.text)
			webhook_answer["sender"] = "bot"
			webhook_answer["receiver"] = "user"
			if not self.question_oracle(json.dumps(webhook_answer)):
				return
			self.wfile.write(bytes(json.dumps(webhook_answer), 'utf8'))

ANSWER_FUNCTIONS_PLACEHOLDER

def run(PORT):
	print("Server launch...")
	httpd = HTTPServer(("", PORT), WebHookResponder)
	httpd.serve_forever()

run(8080)
