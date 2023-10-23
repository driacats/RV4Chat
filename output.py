# Modificato da estendi_classe.py

from http.server import BaseHTTPRequestHandler, HTTPServer
import json

class WebHookResponder(BaseHTTPRequestHandler):

	def do_GET(self):
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()
		messagge = "Hello World!"
		self.wfile.write(bytes(message, 'utf8'))

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



def run(PORT):
	print("Server launch...")
	httpd = HTTPServer(("", PORT), WebHookResponder)
	httpd.serve_forever()

# run(8080)
