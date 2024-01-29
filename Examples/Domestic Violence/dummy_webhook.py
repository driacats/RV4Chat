from aiohttp import web
import json, argparse, asyncio, websockets, time

class Timer():
    def __init__(self, duration):
        self.duration = duration
        self.task = None

    async def wait(self):
        await asyncio.sleep(self.duration)
        print("Sending Help Message to Saved contacts.")

    def start(self):
        if self.task is None:
            self.task = asyncio.create_task(self.wait())

    def stop(self):
        if self.task:
            self.task.cancel()
            self.task = None

delay = 10
timer = Timer(delay)
commit_suicide_counter = 0

answer = "{\"fulfillmentMessages\":[{\"text\":{\"text\":[\"MESSAGE\"]}}], \"bot_action\": \"EVENT\"}"

against_suicide_1_2 = "Your situation seems very difficult and you need help." +\
    " Many victims of violence want to come to an end with their lives," +\
    " and a terribly large share of them do it."+\
    " Please consider to talk with a specialist." +\
    " You can obtain immediate help, in an anonymous way, by calling this help line: ...."

against_suicide_3 = "Please wait, do not do anything irreversible: " +\
    "if you type the help word, I will send a request for help to your contacts."

ask_salary = "Your situation seems very difficult and you might need help." +\
    " There are many anti-violence centers in your city, for example ...." +\
    " Are you independent from an economical point of view?"

ask_children = "Have you children at home?"

async def handle_post(request):

    start_time = time.time() * 1000

    global commit_suicide_counter

    data = await request.json()
    if "queryResult" not in data:
        print("[LOG] Message not valid.")
        return

    # time.sleep(0.02)
    queryResult = data["queryResult"]
    intent = queryResult["intent"]["displayName"]
    entities = {}
    for entity in queryResult["parameters"]:
        entities[entity] = queryResult["parameters"][entity]

    print("[LOG] INTENT:", intent)
    print("[LOG] ENTITIES:", entities)

    time.sleep(0.02)

    if intent == "help_word":
        timer.start()
        final_answer = answer.replace("MESSAGE", "Got it.").replace("BOT_ACTION", "utter")

    elif intent == "undo_word":
        timer.stop()
        final_answer = answer.replace("MESSAGE", "Got it.").replace("BOT_ACTION", "utter")

    elif intent == "commit_suicide":
        commit_suicide_counter += 1
        ifI will kill me commit_suicide_counter < 3:
            final_answer = answer.replace("MESSAGE", against_suicide_1_2).replace("BOT_ACTION", "utter")
        else:
            final_answer = answer.replace("MESSAGE", against_suicide_3).replace("BOT_ACTION", "utter")
        
    elif intent == "get_information":
        final_answer = answer.replace("MESSAGE", ask_salary).replace("BOT_ACTION", "utter")

    elif intent == "inform_chatbot_about_salary":
        final_answer = answer.replace("MESSAGE", ask_children).replace("BOT_ACTION", "utter")

    elif intent == "inform_chatbot_about_salary":
        final_answer = answer.replace("MESSAGE", "Ok, stay safe.").replace("BOT_ACTION", "utter")

    else:
        final_answer = answer.replace("MESSAGE", "Unknown message intent.").replace("BOT_ACTION", "utter")

    # print("[TIME]", time.time() * 1000 - start_time)
    with open("times.csv", "a") as f:
        f.write(str(time.time() * 1000 - start_time) + "\n")
    return web.Response(text=final_answer)

def main():
    parser = argparse.ArgumentParser(prog="Dummy WebHook Server", description="This program simulates a Domestic Violence assistant service")
    parser.add_argument("-p", metavar="rasa|dialogflow", help="Platform to be used for connections.", default="rasa")
    args = parser.parse_args()

    if args.p == "dialogflow":
        app = web.Application()
        app.add_routes([web.post('/', handle_post)])
        web.run_app(app, port=8082)

    if args.p == "rasa":
        print("Rasa")

if __name__ == "__main__":
    main()