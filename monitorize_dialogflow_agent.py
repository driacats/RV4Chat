import json, io, argparse, sys, re
from zipfile import ZipFile
from tqdm import tqdm

class Monitorizer:

    policy_string = """from http.server import BaseHTTPRequestHandler, HTTPServer
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
			message = "{\\"fulfillmentMessages\\":[{\\"text\\":{\\"text\\":[\\"Text response from webhook\\"]}}]}"
			self.wfile.write(bytes(message, 'utf8'))
		if message["intent"]["displayName"] in INTENT_LIST:
			self.wfile.write(bytes(requests.post(YOUR_URL, message)))



def run(PORT):
	print("Server launch...")
	httpd = HTTPServer(("", PORT), WebHookResponder)
	httpd.serve_forever()

run(8080)
"""

    def __init__(self, input_zip, output_zip, URL):
        self.input_zip = ZipFile(input_zip)
        self.output_zip = ZipFile(output_zip, 'w')
        self.intents = {}
        self.json_agent = None
        self.json_package = None
        self.json_intents = []
        self.webHook = ""
        self.URL = URL
    
    def run(self):
        with tqdm(total=4, desc="Progresso") as progress_bar:
            progress_bar.update(1)
            progress_bar.set_description("Loading Dialogflow agent...")
            self.monitorize()
            progress_bar.update(1)
            progress_bar.set_description("Creating monitorized Dialogflow agent...")
            self.write()
            progress_bar.update(1)
            progress_bar.set_description("Generating policy...")
            self.generate_policy()
            progress_bar.update(1)
            progress_bar.set_description("Generated correctly.")

    
    # The function monitorize makes a Dialogflow agent exported as Zip monitorizable
    def monitorize(self):
        # We open the Agent file and take out the webhook url inserted by the user
        self.json_agent = json.loads(self.input_zip.open("agent.json").read())
        self.webHook = self.json_agent["webhook"]["url"]
        # In any case, the new webhook URL is the one provided to the monitorizer
        self.json_agent["webhook"]["url"] = self.URL

        # We store the Package file
        self.json_package = json.loads(self.input_zip.open("package.json").read())
        
        # For each intent
        for name in self.input_zip.namelist():
            if "intents" in name:
                intent = json.loads(self.input_zip.open(name).read())
                if type(intent) is not list:
                    # If the webhook was already used for the intent we store this information
                    # In any case we set the webHookUsed to True
                    if intent["webhookUsed"]:
                        self.intents[intent["name"]] = True
                    else:
                        intent["webhookUsed"] = True
                        self.intents[intent["name"]] = False
                # We append to the intents list the name of the file and the corresponding json
                self.json_intents.append((name, intent))

    # The function write takes the new agent and writes it down inside a new Zip file
    # that can be imported in Dialogflow
    def write(self):
        self.output_zip.writestr("agent.json", json.dumps(self.json_agent))
        self.output_zip.writestr("package.json", json.dumps(self.json_package))
        for (name, intent) in self.json_intents:
            self.output_zip.writestr(name, json.dumps(intent))

    # The function generate_policy generates a policy that :
    #  - monitorize the Dialogflow flow
    #  - sends webhooks to the servers specified by the user
    #  - it does not answer if all goes right
    #  - it answers with an error message if something goes wrong
    # This function modifies the policy python file and saves it in a .py new file.
    def generate_policy(self):
        # policy_in = open("policy_base.py", 'r').read()
        intent_list = "["
        for intent in [intent for intent in self.intents if self.intents[intent]]:
            intent_list += "\"" + intent + "\", "
        intent_list = intent_list[:-2]
        intent_list += "]"
        # If the intent is one of the original webHookUsed ones we need to forward the request
        self.policy_string = self.policy_string.replace("INTENT_LIST", intent_list)
        # We set the webHook original URL for the forwarding
        self.policy_string = self.policy_string.replace("YOUR_URL", "\"" + self.webHook + "\"")
        policy = open("policy.py", "w+")
        policy.write(self.policy_string)
                

def main():
    parser = argparse.ArgumentParser(prog="Monitorize Dialogflow", description="This program makes a Dialogflow agent monitorizable and generates a .py policy")
    parser.add_argument("-i", metavar="input.zip", help="Input file, it should be an exported Dialogflow agent.", required=True)
    parser.add_argument("-o", metavar="output.zip", help="The name of the output zip file for the agent", required=True)
    parser.add_argument("-url", metavar="https://example.address", help="URL of the policy server", required=True)
    args = parser.parse_args()

    if not args.i.endswith(".zip") or not args.o.endswith(".zip"):
        print("Input and/or output file should be .zip files!")
        sys.exit(1)
    url_pattern = re.compile(r'https?://\S+')
    if not bool(url_pattern.match(args.url)):
        print("The url is not valid (does not start with 'http(s)://' )")
        sys.exit(1)
    monitorizer = Monitorizer(args.i, args.o, args.url)
    monitorizer.run()

if __name__ == "__main__":
    main()