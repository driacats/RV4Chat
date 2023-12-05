# File generated automatically on 2023-12-05 17:25 by monitorize_dialogflow_agent.py
#  - Agent: RV4DiagHelloWorld
#  - Input zip: RV4DiagHelloWorld.zip
#  - Output zip: prova.zip
#  - WebHook URL: https://282c-130-251-61-251.ngrok-free.app
#  - Monitor URL: http://127.0.0.1:8081
#  - Monitoring Level: 2


from http.server import BaseHTTPRequestHandler, HTTPServer
import json, requests, random

class WebHookResponder(BaseHTTPRequestHandler):

	MONITOR_URL = "http://127.0.0.1:8081"

	def send_error_message(self):
		message = "{\"fulfillmentMessages\":[{\"text\":{\"text\":[\"Error thrwon from the monitor!\"]}}]}"
		self.wfile.write(bytes(message, 'utf8'))

	def do_POST(self):
		# Accept the request
		content_length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(content_length)
		message = json.loads(post_data)
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		# Send the message to the monitor
		oracle = requests.post(self.MONITOR_URL, json=message).text
		if not oracle:
			# If an error occurred then an error message is sent back
			self.send_error_message()
			return
		if message["queryResult"]["intent"]["displayName"] == "Hello":
			self.hello_answer()
		if message["queryResult"]["intent"]["displayName"] == "Goodbye":
			self.goodbye_answer()
		if message["queryResult"]["intent"]["displayName"] == "Default Fallback Intent":
			self.default_fallback_intent_answer()
		if message["queryResult"]["intent"]["displayName"] == "Default Welcome Intent":
			self.default_welcome_intent_answer()

		# If the intent needs a webhook answer the request is performed
		if message["queryResult"]["intent"]["displayName"] in ["Default Welcome Intent", "Webhook"]:
			self.wfile.write(bytes(requests.post("https://0f99-130-251-61-251.ngrok-free.app", message)))

	def utter_hello_answer(self):
		available_answers = ['Hello!', 'Hey!']
		message = "{\"fulfillmentMessages\":[{\"text\":[\"" + random.choice(available_answers) + "\"]}]}"
		oracle_message = "{\"answer\": \"utter_hello\"}"
		oracle = requests.post(self.MONITOR_URL, json=message)
		if not oracle:
			self.send_error_message()
			return
		self.wfile.write(bytes(message, 'utf8'))

	def utter_goodbye_answer(self):
		available_answers = ['Bye']
		message = "{\"fulfillmentMessages\":[{\"text\":[\"" + random.choice(available_answers) + "\"]}]}"
		oracle_message = "{\"answer\": \"utter_goodbye\"}"
		oracle = requests.post(self.MONITOR_URL, json=message)
		if not oracle:
			self.send_error_message()
			return
		self.wfile.write(bytes(message, 'utf8'))

	def input_unknown_answer(self):
		available_answers = ["I didn't get that. Can you say it again?", 'I missed what you said. What was that?', 'Sorry, could you say that again?', 'Sorry, can you say that again?', 'Can you say that again?', "Sorry, I didn't get that. Can you rephrase?", 'Sorry, what was that?', 'One more time?', 'What was that?', 'Say that one more time?', "I didn't get that. Can you repeat?", 'I missed that, say that again?']
		message = "{\"fulfillmentMessages\":[{\"text\":[\"" + random.choice(available_answers) + "\"]}]}"
		oracle_message = "{\"answer\": \"input_unknown\"}"
		oracle = requests.post(self.MONITOR_URL, json=message)
		if not oracle:
			self.send_error_message()
			return
		self.wfile.write(bytes(message, 'utf8'))

	def input_welcome_answer(self):
		available_answers = ['Hi! How are you doing?', 'Hello! How can I help you?', 'Good day! What can I do for you today?', 'Greetings! How can I assist?']
		message = "{\"fulfillmentMessages\":[{\"text\":[\"" + random.choice(available_answers) + "\"]}]}"
		oracle_message = "{\"answer\": \"input_welcome\"}"
		oracle = requests.post(self.MONITOR_URL, json=message)
		if not oracle:
			self.send_error_message()
			return
		self.wfile.write(bytes(message, 'utf8'))



def run(PORT):
	print("Server launch...")
	httpd = HTTPServer(("", PORT), WebHookResponder)
	httpd.serve_forever()

run(8080)
