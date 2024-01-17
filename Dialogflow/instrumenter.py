import json, io, argparse, sys, re, random, datetime, os
from zipfile import ZipFile
from tqdm import tqdm

class Monitorizer:

    LEVEL_ONE = 1
    LEVEL_TWO = 2

    json_agent = None
    json_package = None
    json_intents = []
    json_entities = []
    intents = {}
    answers = {}
    intent_to_answer = {}
    webHook = ""

    # The __init__ function:
    #   - loads the Dialogflow agent zip exported
    #   - creates the output instrumented Dialogflow agent zip
    #   - stores the level, the URL that will be used by the output policy and the one that will be used by the monitor
    #   - loads the template corresponding to the level
    def __init__(self, input_zip, output_zip, URL, MONITOR_URL, level=LEVEL_ONE):
        self.input_zip = ZipFile(input_zip)
        self.output_zip = ZipFile(os.path.join("output", output_zip), 'w')
        self.level = level
        self.URL = URL
        self.MONITOR_URL = MONITOR_URL
        if level == self.LEVEL_ONE:
            self.policy_string = open("templates/policy_base_level_one.py", 'r').read()
        elif level == self.LEVEL_TWO:
            self.policy_string = open("templates/policy_base_level_two.py", 'r').read()
        else:
            raise ValueError("The inserted level value is not correct. The admissible values are 1 or 2.")
    
    # The function run manages the main workflow of the class:
    #   - it instruments the Dialogflow agent
    #   - if writes the instrumented agent on the output zip
    #   - it generates the policy
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
        self.webHook = self.json_agent["webhook"]["url"].replace("https", "http")
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
                            answer_name = intent["responses"][0]["action"].replace(".", "_")
                            self.intent_to_answer[intent["name"]] = answer_name
                            self.answers[answer_name] = [answer for answer in intent["responses"][0]["messages"][0]["speech"]]
                # We append to the intents list the name of the file and the corresponding json
                self.json_intents.append((name, intent))
            if "entities" in name:
                entity = json.loads(self.input_zip.open(name).read())
                self.json_entities.append((name, entity))

    # The function write takes the new agent and writes it down inside a new Zip file
    # that can be imported in Dialogflow
    def write(self):
        self.output_zip.writestr("agent.json", json.dumps(self.json_agent))
        self.output_zip.writestr("package.json", json.dumps(self.json_package))
        for (name, intent) in self.json_intents:
            self.output_zip.writestr(name, json.dumps(intent))
        for (name, entity) in self.json_entities:
            self.output_zip.writestr(name, json.dumps(entity))

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
        self.policy_string = self.policy_string.replace("INTENT_LIST_PLACEHOLDER", intent_list)
        self.policy_string = self.policy_string.replace("MONITOR_URL_PLACEHOLDER", "\"" + self.MONITOR_URL + "\"")
        # We set the webHook original URL for the forwarding
        self.policy_string = self.policy_string.replace("YOUR_URL_PLACEHOLDER", "\"" + self.webHook + "\"")
        if self.level == self.LEVEL_TWO:
            bot_event_functions = ""
            bot_event_function = open("templates/intent_function.py", "r").read()
            call_functions = ""
            call_function = open("templates/call_function.py", "r").read()
            for intent_answer in self.intent_to_answer:
                if intent_answer not in intent_list:
                    next_action = self.intent_to_answer[intent_answer]
                    new_bef = bot_event_function
                    new_bef = new_bef.replace("INTENT_FUNCTION", next_action.replace(" ", "_").lower())
                    new_bef = new_bef.replace("AVAILABLE_ANSWERS", str(self.answers[next_action]))
                    new_bef = new_bef.replace("NEXT_ACTION", next_action)
                    bot_event_functions += new_bef
                    bot_event_functions += "\n"

                    new_cf = call_function
                    new_cf = new_cf.replace("NEXT_ACTION", next_action.replace(" ", "_").lower())
                    new_cf = new_cf.replace("INTENT", intent_answer)
                    call_functions += new_cf
                    call_functions += "\n"

            self.policy_string = self.policy_string.replace("CALL_ANSWER_FUNCTIONS_PLACEHOLDER", call_functions)
            self.policy_string = self.policy_string.replace("ANSWER_FUNCTIONS_PLACEHOLDER", bot_event_functions)

            header = "# File generated automatically on " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M") + " by " + sys.argv[0] + "\n"
            header += "#  - Agent: " + self.json_agent["displayName"] + "\n"
            header += "#  - Input zip: " + self.input_zip.filename + "\n"
            header += "#  - Output zip: " + self.output_zip.filename + "\n"
            header += "#  - WebHook URL: " + self.URL + "\n"
            header += "#  - Monitor URL: " + self.MONITOR_URL + "\n"
            header += "#  - Monitoring Level: " + str(self.level) + "\n"
            self.policy_string = header + "\n\n" + self.policy_string

        policy = open("output/policy.py", "w+")
        policy.write(self.policy_string)
                

def main():
    parser = argparse.ArgumentParser(prog="Monitorize Dialogflow", description="This program makes a Dialogflow agent monitorizable and generates a .py policy")
    parser.add_argument("-i", metavar="input.zip", help="Input file, it should be an exported Dialogflow agent.", required=True)
    parser.add_argument("-o", metavar="output.zip", help="The name of the output zip file for the agent", required=True)
    parser.add_argument("-url", metavar="https://example.address", help="URL of the policy server", required=True)
    parser.add_argument("-murl", metavar="ws://monitor.address", help="URL of the monitor to query", required=True)
    parser.add_argument("-level", metavar="n", type=int, help="Level of monitoring to gain. 1 for user messages, 2 for user and chatbot messages.", default=1)
    args = parser.parse_args()

    if not args.i.endswith(".zip") or not args.o.endswith(".zip"):
        print("Input and/or output file should be .zip files!")
        sys.exit(1)
    url_pattern = re.compile(r'https?://\S+')
    murl_pattern = re.compile(r'ws://\S+')
    if not bool(url_pattern.match(args.url)):
        print("The url is not valid (does not start with 'http(s)://' )")
        sys.exit(1)
    if not bool(murl_pattern.match(args.murl)):
        print("The monitor url is not valid (does not start with 'http(s)://' )")
        sys.exit(1)
    if args.level not in (1, 2):
        print("The provided level is not admissible. It should wither 1 or 2.")
        sys.exit(1)
    monitorizer = Monitorizer(args.i, args.o, args.url, args.murl, args.level)
    monitorizer.run()

if __name__ == "__main__":
    main()
