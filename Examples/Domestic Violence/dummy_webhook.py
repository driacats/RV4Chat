from aiohttp import web
import json, argparse, asyncio, websockets, time

# The Timer class is able to start and stop a timer of a given time
class Timer():

    # The init function takes as argument the duration of the timer
    def __init__(self, duration):
        self.duration = duration
        self.task = None

    # Wait simply waits duration seconds
    async def wait(self):
        await asyncio.sleep(self.duration)
        print("Sending Help Message to Saved contacts.")

    # start function makes the counter start
    def start(self):
        if self.task is None:
            self.task = asyncio.create_task(self.wait())

    # stop function stops the function
    def stop(self):
        if self.task:
            self.task.cancel()
            self.task = None

# Global variables
delay = 10 # Seconds to wait
timer = Timer(delay) # Timer of delay seconds
commit_suicide_counter = 0 # counter of times the user wants to commit suicide

# Global answer strings
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

# The fucnction handle_msg takes as input:
#   - msg: {intent: _, entities: {e1: _, e2: _, ...}}
# and returns two answers:
#   - final_answer: the string to be displayed for the user
#   - bot_event: the event to be used for the Monitor
async def handle_msg(msg):
    # Makes the variable accessible
    global commit_suicide_counter

    # Loads the json message
    msg = json.loads(msg)

    # Load intent and entities
    intent = msg["intent"]
    entities = msg["entities"]

    print("[LOG] INTENT:", intent)
    print("[LOG] ENTITIES:", entities)

    # Wait 20 milliseconds
    time.sleep(0.02)

    # Choose action depending on intent
    if intent == "help_word":
        timer.start()
        final_answer = ("Got it.", "utter_help")
    elif intent == "undo_word":
        timer.stop()
        final_answer = ("Got it.", "utter_help")

    elif intent == "commit_suicide":
        commit_suicide_counter += 1
        if commit_suicide_counter < 3:
            final_answer = (against_suicide_1_2, "utter_against_suicide")
        else:
            final_answer = (against_suicide_3, "utter_against_suicide")
    elif intent == "get_information":
        final_answer = (ask_salary, "utter_ask_salary")
    elif intent == "inform_chatbot_about_salary":
        final_answer = (ask_children, "utter_ask_children")
    elif intent == "inform_chatbot_about_children":
        final_answer = ("Ok, stay safe", "utter_normal")
    else:
        final_answer = ("Unknown message.", "utter_unknown")

    return final_answer

# The handle_post function manages the POST requests
async def handle_post(request):

    start_time = time.time() * 1000

    # Load the json message
    data = await request.json()
    # Check if it is a valid Dialogflow message
    if "queryResult" not in data:
        print("[LOG] Message not valid.")
        return

    # Build the message in the form
    # {intent: _, entities: {e1: _, e2: _, ...}}
    # for the handle_msg function
    request = {}
    queryResult = data["queryResult"]
    intent = queryResult["intent"]["displayName"]
    entities = {}
    for entity in queryResult["parameters"]:
        entities[entity] = queryResult["parameters"][entity]
    
    request["intent"] = intent
    request["entities"] = entities

    # Compute the answer and the bot event
    (final_answer, bot_event) = await handle_msg(json.dumps(request))
    # Build the answer for Dialogflow
    final_answer = answer.replace("MESSAGE", final_answer).replace("EVENT", bot_event)

    # Compute time
    with open("times.csv", "a") as f:
        f.write(str(time.time() * 1000 - start_time) + "\n")

    # Send back the message to be displayed
    return web.Response(text=final_answer)


# The handle_ws function manages WebSocket connections
async def handle_ws(request):

    # Create a server that waits for messages
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # For each message received handle
    # the message and compute the answer
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            (final_answer, bot_event) = await handle_msg(msg.data)
            await ws.send_str(str((final_answer, bot_event)))
            
    return ws

def main():
    parser = argparse.ArgumentParser(prog="Dummy WebHook Server", description="This program simulates a Domestic Violence assistant service")
    parser.add_argument("-p", metavar="rasa|dialogflow", help="Platform to be used for connections.", default="rasa")
    args = parser.parse_args()

    if args.p == "dialogflow":
        app = web.Application()
        app.add_routes([web.post('/', handle_post)])
        web.run_app(app, port=8082)

    if args.p == "rasa":
        app = web.Application()
        app.add_routes([web.get('/', handle_ws)])
        web.run_app(app, port=8082)

if __name__ == "__main__":
    main()