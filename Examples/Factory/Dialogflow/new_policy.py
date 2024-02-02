from aiohttp import web
import json, websockets, urllib3

class Oracle:

    MONITOR_URL = "ws://localhost:5052"
    oracle = websockets.connect(MONITOR_URL)

    error = "{\"fulfillmentMessages\":[{\"text\":{\"text\":[\"Error thrwon from the monitor!\"]}}]}"

    def question(event):
        print("[POLICY]", event)
        await oracle.send(event)
        answer = await oracle.recv()
        return answer['verdict']

class ConversationFlow:

    def __init__(self):
        self.oracle = Oracle()
        self.trace = []
        self.http = urllib3.PoolManager()

    def next_event(self, event, msg):
        # Compute the next action: if the message is a user one
        # calls the webhook and manages the output
        if event['sender'] == 'bot':
            return None
        if event['intent']['name'] in ['add_object', 'remove_object', 'add_relative_object']:
            new_event = self.http.request('POST', 'http://localhost:8082', body=json.dumps(msg))
            new_event = json.loads(new_event.data)
            new_event['sender'] = 'bot'
            new_event['receiver'] = 'user'
            return new_event

    def consume_event(self, event):
        # Consume event means look if the event is correct for the monitor
        if not self.oracle.question(event):
            return False
        # Something more?
        return True

    def manage_flow(self, event, msg):
        # for each new message:
        # 1. consume the event
        # 2. while there is a next:
        #   2.1 consume next event
        if not self.consume_event(event):
            raise RuntimeError("[POLICY] Error thrown from the monitor.")
        event = self.next_event(event, msg)
        while(event is not None):
            if not self.consume_event(event):
                raise RuntimeError("[POLICY] Error thrown from the monitor.")
            event = self.next_event(event, msg)
        

def msg2event(msg):
    msg_json = {}
    if 'queryResult' in msg:
        queryResult = msg['queryResult']
        msg_json['sender'] = 'user'
        msg_json['receiver'] = 'bot'
        
        intent = {}
        intent['name'] = queryResult['intent']['displayName']
        intent['confidence'] = queryResult['intentDetectionConfidence']
        msg_json['intent'] = intent
        
        entities = {}
        for entity in queryResult['parameters']:
            entities[entity] = queryResult['parameters'][entity]
        msg_json['entities'] = entities
    
    else:
        msg_json = msg
        msg_json['sender'] = 'bot'
        msg_json['receiver'] = 'user'
        
        return json.dumps(msg_json)

flow = ConversationFlow()

async def handle_post(request):
    
    data = await request.json()
    data = json.loads(data)

    event = msg2event(data)

def main():
    parser = argparse.ArgumentParser(prog="Dialogflow Policy", description="This program executes the Dialogflow policy.")
    parser.add_argument("-p", "--port", metavar="PORT", help="Port on which send messages", default="8080")
    args = parser.parse_args()

    app = web.Application()
    app.add_routes([web.post('/', lambda request: handle_post(request, args.port))])
    web.run_app(app, port=args.port)

if __name__ == "__main__":
    main()