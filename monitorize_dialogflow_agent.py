import json
from zipfile import ZipFile

class Monitorizer:

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
        self.monitorize()
        self.write()
        self.generate_policy()
    
    def monitorize(self):
        agent = json.loads(self.input_zip.open("agent.json").read())
        self.webHook = agent["webhook"]["url"]
        agent["webhook"]["url"] = self.URL

        self.json_agent = agent
        self.json_package = json.loads(self.input_zip.open("package.json").read())
        
        for name in self.input_zip.namelist():
            if "intents" in name:
                intent = json.loads(self.input_zip.open(name).read())
                if type(intent) is not list:
                    if intent["webhookUsed"]:
                        self.intents[intent["name"]] = True
                    else:
                        intent["webhookUsed"] = True
                        self.intents[intent["name"]] = False
                self.json_intents.append((name, intent))

    def write(self):
        self.output_zip.writestr("agent.json", json.dumps(self.json_agent))
        self.output_zip.writestr("package.json", json.dumps(self.json_package))
        for (name, intent) in self.json_intents:
            self.output_zip.writestr(name, json.dumps(intent))

    def generate_policy(self):
        pass
                

monitorizer = Monitorizer("./RV4DiagHelloWorld.zip", "./output.zip", "MY_NEW_URL")
monitorizer.run()