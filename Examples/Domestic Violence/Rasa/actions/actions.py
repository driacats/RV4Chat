from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import SlotSet
import json, time, threading, requests
from websocket import create_connection

class send_request(Action):

    server = "ws://localhost:8082"

    def name(self) -> Text:
        return "send_request"

    def run(self, dispatcher, tracker, domain):
        
        msg = tracker.latest_message

        request = {}
        request['sender'] = 'user'
        request['intent'] = msg['intent']['name']

        entities = {}
        for entity in msg['entities']:
            e_name = entity['entity']
            entities[e_name] = entity['value']
        
        request['entities'] = entities

        ws = create_connection(self.server)
        print('connection created...')
        ws.send(json.dumps(request))
        print('sending...')
        (answer, bot_event) = eval(ws.recv())
        print('getting the result: ', answer)
        ws.close()
        dispatcher.utter_message(text=answer)
        return [SlotSet('bot_event', bot_event)]

# class wait(Action):

#     seconds = 5

#     def name(self) -> Text:
#         return 'wait'

#     def run(self, dispatcher, tracker, domain):
#         time.sleep(seconds)
#         return [SlotSet('bot_event', 'wait')]

class wait(Action):

    server = 'ws://localhost:8082'

    def name(self) -> Text:
        return 'wait'

    def run(self, dispatcher, tracker, domain):
        dispatcher.utter_message(text='Got it.')
        threading.Thread(target=self.wait, args=(dispatcher,)).start()

    def wait(self, dispatcher):
        ws = create_connection(self.server)
        print('connection created...')
        request = {}
        request['sender'] = 'bot'
        request['action'] = 'check_wait'
        answer = False
        while not answer:
            ws.send(json.dumps(request))
            print('sending...')
            (answer, bot_event) = eval(ws.recv())
            print('getting the result: ', answer)
            time.sleep(1)
        ws.close()
        # dispatcher.utter_message(text='The sun is bright today!')
        # requests.post('http://localhost:8888', json={'sender': 'bot', 'msg': 'The sun is bright today!'})
        return [SlotSet('bot_event', bot_event)]

class send_bot_msg(Action):

    server = 'http://localhost:8888'

    def name(self) -> Text:
        return 'send_bot_msg'

    def run(self, dispatcher, tracker, domain):
        requests.post(self.server, json={'sender': 'bot', 'msg': 'The sun is bright today!'})
        return [SlotSet('bot_event', 'help_called')]