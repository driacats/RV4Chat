import json
from zipfile import ZipFile

input_zip = ZipFile("./RV4DiagHelloWorld.zip")
output_zip = ZipFile("./output.zip", "w")


intents = []
agent_name = json.loads(input_zip.open("agent.json").read())["displayName"]

monitor = open(agent_name + "Policy.py", "w+")
monitor.write()

for name in input_zip.namelist():
    if "intents" in name:
        f = input_zip.open(name)
        content = json.loads(f.read())
        print("=======================" + name + "=======================")
        print(json.dumps(content, indent=2))
        # intents.append(content["name"])
        # print(intents)
        # output_zip.writestr(name, json.dumps(content))
        # for key in content:
print(intents)
            

# print(agent)