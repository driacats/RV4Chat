# File generated automatically on 2024-01-16 12:41 by instrumenter.py
#  - Agent: AssistantAgent
#  - Input zip: Examples/Factory/AssistantAgent.zip
#  - Output zip: output/AssistantAgentMonitored.zip
#  - WebHook URL: https://7540-130-251-61-251.ngrok-free.app
#  - Monitor URL: ws://localhost:8081
#  - Monitoring Level: 2


# IMPORTS
from http.server import BaseHTTPRequestHandler, HTTPServer
import json, random, time
import urllib3
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
			if param == "Object":
				entities["object"] = message["queryResult"]["parameters"][param]
			else:
				entities[param] = message["queryResult"]["parameters"][param]
			if param in ["posX", "posY"] and message["queryResult"]["parameters"][param] == "":
				entities[param] = "center"
		json_obj["entities"] = entities
		return json.dumps(json_obj)

	def question_oracle(self, event_str):
		# ws = create_connection(self.MONITOR_URL)
		# We send it to the monitor and wait for the answer.
		print("[LOG] " + event_str)
		self.ws.send(event_str)
		oracle = json.loads(self.ws.recv())
		# self.ws.close()
		# print("[EVENT]", event_str)
		# print("[ORACLE]", oracle)
		if not oracle["verdict"]:
			self.send_error_message()
			return False
		return True

	def do_POST(self):
		print("[LOG] New message")
		times = []
		start_time = time.time() * 1000
		# Accept the request
		content_length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(content_length)
		message = json.loads(post_data)
		user_event = self.msg2json(message)
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		# print("[TIME] Header", round(time.time() * 1000 - start_time, 2))
		times.append(round(time.time() * 1000 - start_time, 2))
		# Send the user input event to the monitor
		if not self.question_oracle(user_event):
			return
		# print("[TIME] Oracle user", round(time.time() * 1000 - start_time, 2))
		times.append(round(time.time() * 1000 - start_time, 2))

		# If the intent needs a webhook answer the request is performed
		if message["queryResult"]["intent"]["displayName"] in ["add_object", "remove_object", "add_relative_object"]:
			# webhook_answer = requests.post("http://localhost:8082", json=message)
			webhook_answer = self.http.request('POST', "http://localhost:8082", body=json.dumps(message))
			# print(webhook_answer.data)
			# print("[TIME] Action", round(time.time() * 1000 - start_time, 2))
			times.append(round(time.time() * 1000 - start_time, 2))
			webhook_answer = json.loads(webhook_answer.data)
			webhook_answer["sender"] = "bot"
			webhook_answer["receiver"] = "user"
			if not self.question_oracle(json.dumps(webhook_answer)):
				return
			# print("[TIME] Oracle bot", round(time.time() * 1000 - start_time, 2))
			times.append(round(time.time() * 1000 - start_time, 2))

			self.wfile.write(bytes(json.dumps(webhook_answer), 'utf8'))
			# print("[TIME]", round(time.time() * 1000 - start_time, 2))
			times.append(round(time.time() * 1000 - start_time, 2))
			print("[TIMES]", times)



def run(PORT):
	print("Server launch...")
	httpd = HTTPServer(("", PORT), WebHookResponder)
	httpd.serve_forever()

run(8080)
