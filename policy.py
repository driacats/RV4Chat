from http.server import BaseHTTPRequestHandler, HTTPServer
import json, requests

class WebHookResponder(BaseHTTPRequestHandler):

	def do_POST(self):
		content_length = int(self.headers['Content-Length'])
		post_data = self.rfile.read(content_length)
		message = json.loads(post_data)
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		if "Hello" in message["queryResult"]["queryText"]:
			message = "{\"fulfillmentMessages\":[{\"text\":{\"text\":[\"Text response from webhook\"]}}]}"
			self.wfile.write(bytes(message, 'utf8'))
		if message["intent"]["displayName"] in ["Default Welcome Intent", "Webhook"]:
			self.wfile.write(bytes(requests.post("https://a522-130-251-61-251.ngrok-free.app", message)))



def run(PORT):
	print("Server launch...")
	httpd = HTTPServer(("", PORT), WebHookResponder)
	httpd.serve_forever()

run(8080)
