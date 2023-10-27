class WebHookResponder(BaseHTTPRequestHandler):

	MONITOR_URL = MONITOR_URL_PLACEHOLDER

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
		# If the intent needs a webhook answer the request is performed
		if message["queryResult"]["intent"]["displayName"] in INTENT_LIST_PLACEHOLDER:
			self.wfile.write(bytes(requests.post(YOUR_URL_PLACEHOLDER, message)))

def run(PORT):
	print("Server launch...")
	httpd = HTTPServer(("", PORT), WebHookResponder)
	httpd.serve_forever()

run(8080)
