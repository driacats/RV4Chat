# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List
#
# from rasa_sdk import Action, Tracker
# from rasa_sdk.executor import CollectingDispatcher
#
#
# class ActionHelloWorld(Action):
#
#     def name(self) -> Text:
#         return "action_hello_world"
#
#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
#
#         dispatcher.utter_message(text="Hello World!")
#
#         return []

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import json
from websocket import create_connection

class send_request(Action):

    server = "ws://localhost:8082"

    def name(self) -> Text:
        return "send_request"

    def run(self, dispatcher, tracker, domain):
        
        msg = tracker.latest_message

        request = {}

        request["intent"] = msg["intent"]["name"]

        entities = {}
        for entity in msg["entities"]:
            e_name = entity["entity"]
            entities[e_name] = entity["value"]
        
        request["entities"] = entities

        ws = create_connection(self.server)
        print("connection created...")
        ws.send(json.dumps(request))
        print("sending...")
        (answer, bot_event) = eval(ws.recv())
        print("getting the result: ", answer)
        ws.close()
        dispatcher.utter_message(text=answer)
        return [SlotSet("bot_event", bot_event)]