from http.server import BaseHTTPRequestHandler, HTTPServer
import json, requests

class Monitor(BaseHTTPRequestHandler):

    def do_POST(self):
        # Accept the request
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        message = json.loads(post_data)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        print("[LOG]", message)
        self.wfile.write(bytes(True))
        # if "queryResult" in message:
        #     print("user said: ", message["queryResult"]["queryText"])
        #     if "e" in message["queryResult"]["queryText"]:
        #         print("False!")
        #         self.wfile.write(bytes(False))
        #     else:
        #         print("True!")
        #         self.wfile.write(bytes(True))
        # else:
        #     print(message)

def run(PORT):
    print("Server launch...")
    httpd = HTTPServer(("localhost", PORT), Monitor)
    httpd.serve_forever()

run(8081)