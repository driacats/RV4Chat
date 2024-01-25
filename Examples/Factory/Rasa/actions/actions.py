# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

#from rasa_sdk import Action, Tracker
from rasa_sdk import Action
from rasa_sdk.events import AllSlotsReset, SlotSet
#from rasa_sdk.executor import CollectingDispatcher
#import socket
import json, time
from websocket import create_connection

class ActionResetAllSlots(Action):

    def name(self):
        return "action_reset_all_slots"

    def run(self, dispatcher, tracker, domain):
        with open("times.log", 'a') as f:
            f.write("[RESET]" + str(time.time() * 1000) + "\n")
        # print("[TIME]", time.time() * 1000)
        return [AllSlotsReset()]

class SendInfo(Action):

    mas_server = "ws://localhost:8082"

    def name(self):
        return "send_info"
    
    def run(self, dispatcher, tracker, domain):
        with open("times.log", 'a') as f:
            f.write("[SEND]" + str(time.time() * 1000) + "\n")
        # print("[TIME]", time.time() * 1000)
        instruction = {}
        instruction['intent'] = tracker.latest_message['intent'].get('name')
        instruction['obj'] = tracker.get_slot('object')
        if instruction['intent'] in ('add_object', 'add_actor') and tracker.get_slot('horizontal') is None:
            instruction['posX'] = 'center'
        else:
            instruction['posX'] = tracker.get_slot('horizontal')
        if instruction['intent'] in ('add_object', 'add_actor') and tracker.get_slot('vertical') is None:
            instruction['posY'] = 'center'
        else:
            instruction['posY'] = tracker.get_slot('vertical')
        instruction['relPos'] = tracker.get_slot('relative')
        instruction['relName'] = tracker.get_slot('relName')
        instruction['actorName'] = tracker.get_slot('actorName')
        ws = create_connection(self.mas_server)
        print("connection created...")
        ws.send(json.dumps(instruction))
        print("sending...")
        result = ws.recv()
        print("getting the result: ", result)
        ws.close()
        return [SlotSet("webhookResult", result.split()[-1])]

# class GetTime(Action):

#     def name(self):
#         return "get_time"

#     def run(self, dispatcher, tracker, domain):
#         print("[LOG] ", time.time() * 1000)