import json, io, argparse, sys, re, random
from zipfile import ZipFile
from tqdm import tqdm

class Monitorizer:

    LEVEL_ONE = 1
    LEVEL_TWO = 2

    json_agent = None
    json_package = None
    json_intents = []
    intents = {}
    answers = {}
    webHook = ""

    def __init__(self, input_zip, output_zip, URL, level=1):
        self.input_zip = ZipFile(input_zip)
        self.output_zip = ZipFile(output_zip, 'w')
        self.level = level
        self.URL = URL
        if level == self.LEVEL_ONE:
            self.policy_string = open("policy_base_level_one.py", 'r').read()
        elif level == self.LEVEL_TWO:
            self.policy_string = open("policy_base_level_two.py", 'r').read()
        else:
            raise ValueError("The inserted level value is not correct. The admissible values are 1 or 2.")
    
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
                    if self.level == self.LEVEL_TWO:
                        if "speech" in intent["responses"][0]["messages"][0]:
                            # self.answers[name[8:-5].replace(" ", "_")] = [answer for answer in intent["responses"][0]["messages"][0]["speech"]]
                            self.answers[intent["name"]] = [answer for answer in intent["responses"][0]["messages"][0]["speech"]]
                        # else:
                        #     self.answers[name[8:-5].replace(" ", "_")] = []
                # We append to the intents list the name of the file and the corresponding json
                self.json_intents.append((name, intent))

        # print(self.answers)

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
        intent_list = "["
        for intent in [intent for intent in self.intents if self.intents[intent]]:
            intent_list += "\"" + intent + "\", "
        intent_list = intent_list[:-2]
        intent_list += "]"
        # If the intent is one of the original webHookUsed ones we need to forward the request
        self.policy_string = self.policy_string.replace("INTENT_LIST", intent_list)
        # We set the webHook original URL for the forwarding
        self.policy_string = self.policy_string.replace("YOUR_URL", "\"" + self.webHook + "\"")
        if self.level == self.LEVEL_TWO:
            answer_functions = ""
            call_functions = ""
            for intent_answer in self.answers:
                answer_functions += "\tdef " + intent_answer.replace(" ", "_").lower() + "_answer(self):\n"
                answer_functions += "\t\tmessage = \"{\\\"fulfillmentMessages\\\":[{\\\"text\\\":[\\\"" + random.choice(self.answers[intent_answer]) + "\\\"]}]}\"\n"
                answer_functions += "\t\tself.wfile.write(bytes(message, \'utf8\'))\n\n"

                call_functions += "\t\tif message[\"intent\"][\"displayName\"] == \"" + intent_answer + "\":\n"
                call_functions += "\t\t\tself." + intent_answer.replace(" ", "_").lower() + "_answer()\n"
            self.policy_string = self.policy_string.replace("CALL_ANSWER_FUNCTIONS", call_functions)
            self.policy_string = self.policy_string.replace("ANSWER_FUNCTIONS", answer_functions)
        # print(call_functions)
        # print(answer_functions)
        policy = open("policy.py", "w+")
        policy.write(self.policy_string)
                

def main():
    parser = argparse.ArgumentParser(prog="Monitorize Dialogflow", description="This program makes a Dialogflow agent monitorizable and generates a .py policy")
    parser.add_argument("-i", metavar="input.zip", help="Input file, it should be an exported Dialogflow agent.", required=True)
    parser.add_argument("-o", metavar="output.zip", help="The name of the output zip file for the agent", required=True)
    parser.add_argument("-url", metavar="https://example.address", help="URL of the policy server", required=True)
    parser.add_argument("-level", metavar="n", type=int, help="Level of monitoring to gain. 1 for user messages, 2 for user and chatbot messages.", default=1)
    args = parser.parse_args()

    if not args.i.endswith(".zip") or not args.o.endswith(".zip"):
        print("Input and/or output file should be .zip files!")
        sys.exit(1)
    url_pattern = re.compile(r'https?://\S+')
    if not bool(url_pattern.match(args.url)):
        print("The url is not valid (does not start with 'http(s)://' )")
        sys.exit(1)
    if args.level not in (1, 2):
        print("The provided level is not admissible. It should wither 1 or 2.")
        sys.exit(1)
    monitorizer = Monitorizer(args.i, args.o, args.url, args.level)
    monitorizer.run()

if __name__ == "__main__":
    main()