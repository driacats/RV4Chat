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
        return [AllSlotsReset()]

class SendInfo(Action):

    mas_server = "ws://localhost:8082"

    def name(self):
        return "send_info"
    
    def run(self, dispatcher, tracker, domain):
        instruction = {}
        instruction['intent'] = tracker.latest_message['intent'].get('name')
        entities = {}
        entities['object'] = tracker.get_slot('object')
        if instruction['intent'] in ('add_object', 'add_actor') and tracker.get_slot('horizontal') is None:
            entities['posX'] = 'center'
        else:
            entities['posX'] = tracker.get_slot('horizontal')
        if instruction['intent'] in ('add_object', 'add_actor') and tracker.get_slot('vertical') is None:
            entities['posY'] = 'center'
        else:
            entities['posY'] = tracker.get_slot('vertical')
        entities['relPos'] = tracker.get_slot('relative')
        if instruction['intent'] == 'remove_object':
            entities['relname'] = tracker.get_slot('relName')
        else:
            entities['relName'] = tracker.get_slot('relName')
        entities['actorName'] = tracker.get_slot('actorName')
        instruction['entities'] = entities
        ws = create_connection(self.mas_server)
        print("connection created...")
        ws.send(json.dumps(instruction))
        print("sending...")
        result = ws.recv()
        print("getting the result: ", result)
        ws.close()
        return [SlotSet("webhookResult", result.split()[-1])]