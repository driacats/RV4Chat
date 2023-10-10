from http.server import BaseHTTPRequestHandler, HTTPServer

class WebHookResponder(BaseHTTPRequestHandler):

    def do_GET(self):
        print("do_GET")

    def do_POST(self):
        


def run(PORT):
    print("Server launch...")
    httpd = HTTPServer(("", PORT), WebHookResponder)
    httpd.serve_forever()
    
run(8080)