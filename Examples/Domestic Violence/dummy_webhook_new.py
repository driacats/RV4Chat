from http.server import BaseHTTPRequestHandler, HTTPServer
import json, requests, argparse, asyncio, websockets, time, threading



# The FactoryWebHookHttp class implements a listener server in Http.
# It is used with Dialogflow (to respect the WebHook API).
class DomesticViolenceWebHookHttp(BaseHTTPRequestHandler):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.timer = None
    # timer = None

    start_time = -1

    answer = "{\"fulfillmentMessages\":[{\"text\":{\"text\":[\"MESSAGE\"]}}], \"bot_action\": \"EVENT\", \"aux\": {AUX}}"
    delay = 10
    commit_suicide_counter = 0
    
    against_suicide_1_2 = "Your situation seems very difficult and you need help."
    against_suicide_1_2 += " Many victims of violence want to come to an end with their lives, and a terribly large share of them do it."
    against_suicide_1_2 += " Please consider to talk with a specialist. You can obtain immediate help, in an anonymous way, by calling this help line: ...."

    against_suicide_3 = "Please wait, do not do anything irreversible: if you type the help word, I will send a request for help to your contacts."

    ask_salary = "Your situation seems very difficult and you might need help. There are many anti-violence centers in your city, for example ...."
    ask_salary += "Are you independent from an economical point of view?"

    ask_children = "Have you children at home?"

    # def wait_for_delay(self):
        # self.timer = threading.Timer(self.delay, self.send_help_messages)  # Timer di 10 secondi
        # self.timer.start()
        # print(self.timer)
    
    def send_help_messages(self):
        print("Sending Help Messaged to Saved contacts.")

    def do_POST(self):
        start_time = time.time() * 1000
        # Accept the request
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        message = json.loads(post_data)
        time.sleep(0.02)

        if not "queryResult" in message:
             print("[LOG] Message not valid.")
             return

        # Get intent and entities from the request
        intent = message["queryResult"]["intent"]["displayName"]
        entities = {}
        for entity in message["queryResult"]["parameters"]:
            entities[entity] = message["queryResult"]["parameters"][entity]

        print("[LOG] INTENT:", intent)
        print("[LOG] ENTITIES:", entities)

        if intent == "help_word":
            # self.wait_for_delay()
            self.timer = threading.Timer(self.delay, self.send_help_messages)  # Timer di 10 secondi
            self.timer.start()
        
        elif intent == "undo_word":
            # print(self.timer)
            if self.timer and self.timer.is_alive():
                self.timer.cancel()
        
        elif intent == "commit_suicide":
            if self.commit_suicide_counter < 2:
                print(self.against_suicide_1_2)
            else:
                print(self.against_suicide_3)
        
        elif intent == "get_information":
            print(self.ask_salary)
        
        elif intent == "inform_chatbot_about_salary":
            print(self.ask_children)



        # Send the answer
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(bytes(self.answer.replace("MESSAGE", "Got it!").replace("EVENT", "None").replace("AUX", ""), 'utf8'))

        print("[TIME]", time.time() * 1000 - start_time)

def FactoryWebHookWebSocket():

    factory = Factory()

    async def echo(websocket, path):
        # Print a message when a new connection is established
        print(f"New connection from {websocket.remote_address}")

        try:
            # Loop to handle messages received from the connection
            async for message in websocket:
                # Print the received message
                print(f"Received message: {message}")
                message = json.loads(message)

                if message["intent"] == "add_object":
                    if factory.add_object(message["obj"], message["posX"], message["posY"]):
                        obj_name = message["obj"] + str(factory.counter[message["obj"]])
                        answer = "Object added, you can refer to as " + obj_name
                    else:
                        answer = "Error in adding object"
                if message["intent"] == "add_relative_object":
                    if factory.add_relative_object(message["obj"], message["relName"], message["relPos"]):
                        obj_name = message["obj"] + str(factory.counter[message["obj"]])
                        answer = "Object added, you can refer to as " + obj_name
                    else:
                        answer = "Error in adding object"
                if message["intent"] == "remove_object":
                    if factory.remove_object(message["relName"]):
                        answer = "Object removed"
                    else:
                        answer = "Error in adding object"

                # Respond always with "true"
                # response = "{\"verdict\": true}"

                factory.print_factory()

                # Send the response back to the client
                await websocket.send(answer)
                print(f"Sent response: {answer}")

        except websockets.exceptions.ConnectionClosed:
            # Handle connection closure
            print(f"Connection closed by {websocket.remote_address}")

    # Start the WebSocket server
    start_server = websockets.serve(echo, "localhost", 8082)

    # Run the server in an infinite loop
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

def main():
    parser = argparse.ArgumentParser(prog="Dummy WebHook Server", description="This program simulates a factory CAD service")
    parser.add_argument("-p", metavar="rasa|dialogflow", help="Platform to be used for connections.", default="rasa")
    args = parser.parse_args()

    if args.p == "dialogflow":
        print("Server launch...")
        httpd = HTTPServer(("localhost", 8082), DomesticViolenceWebHookHttp)
        httpd.serve_forever()
    elif args.p == "rasa":
        print("Server launch...")
        wsd = FactoryWebHookWebSocket()

if __name__ == "__main__":
    main()