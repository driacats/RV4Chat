from http.server import BaseHTTPRequestHandler, HTTPServer
import json, requests

class WebHookResponder(BaseHTTPRequestHandler):

	def do_POST(self):
		# Accept the request
		content_length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(content_length)
		message = json.loads(post_data)
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		# Send the message to the monitor
		oracle = requests.post(MONITOR_URL, json=message)
		if not oracle:
			# Answer Dialogflow if the monitor returns true
			message = "{\"fulfillmentMessages\":[{\"text\":{\"text\":[\"Error message from monitor\"]}}]}"
			self.wfile.write(bytes(message, 'utf8'))
			return
		# If the intent needs a webhook answer the request is performed
		if message["intent"]["displayName"] in INTENT_LIST:
			self.wfile.write(bytes(requests.post(YOUR_URL, message)))



def run(PORT):
	print("Server launch...")
	httpd = HTTPServer(("", PORT), WebHookResponder)
	httpd.serve_forever()

run(8080)
