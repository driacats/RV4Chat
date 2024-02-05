from aiohttp import web
from websocket import create_connection
import urllib3, json

MONITOR_URL = 'ws://localhost:5052'
WEBHOOK_URL = 'http://localhost:8082'

webhook = urllib3.PoolManager()

def create_user_event(msg):
    queryResult = msg['queryResult']
    event = {}
    
    # Header
    event['sender'] = 'user'
    event['receiver'] = 'bot'

    # Intent
    intent = {}
    intent['name'] = queryResult['intent']['displayName']
    intent['confidence'] = queryResult['intentDetectionConfidence']

    event['intent'] = intent
    
    # Entities
    entities = {}
    for entity in queryResult['parameters']:
        entities[entity] = queryResult['parameters'][entity]

    event['entities'] = entities

    return event

def create_bot_event(msg):
    # In the case of bot event the msg comes fromt the bot
    # and not from Dialogflow. In this case we assume that
    # the message is already formatted in a monitorizable way
    # and that we have only to add sender, receiver and event if needed.
    # Other parameters can change a lot depending on the action.
    event = msg
    if 'sender' not in event:
        event['sender'] = 'bot'
    if 'receiver' not in event:
        event['receiver'] = 'user'
    if 'bot_action' not in event:
        event['bot_action'] = 'unknown_event'

    return event

def create_event(msg):
    if 'queryResult' in msg:
        return create_user_event(msg)
    return create_bot_event(msg)

def ask_monitor(event):
    print(f'[POLICY]\tLOG\t Connecting to {MONITOR_URL}')
    ws = create_connection(MONITOR_URL)
    print('[POLICY]\tLOG\t Connection created')
    ws.send(json.dumps(event))
    print('[POLICY]\tLOG\t Message sent.')
    oracle = json.loads(ws.recv())
    # print(f'[POLICY]\tLOG\t Oracle raw value is {oracle}')
    ws.close()
    print(f'[POLICY]\tLOG\t Verdict: {oracle["verdict"]}')
    return oracle['verdict']

def ask_webhook(msg):
    next_event = webhook.request('POST', WEBHOOK_URL, body=json.dumps(msg))
    next_event = load_json_post(next_event.data)
    return create_event(next_event)

def next_event(event):
    # print(f'[POLICY]\tLOG\t Got {type(event)} {event}')
    if (event['sender'] == 'bot'):
        return None
    if (event['intent']['name'] in ['add_object', 'remove_object', 'add_relative_object']):
        return 'ask_webhook'

def consume_event(event, msg):
    oracle = ask_monitor(event)
    if not oracle:
        raise RuntimeError('[POLICY]\tERR\t Error raised by the monitor.')
    # print(f'[POLICY]\tLOG\t Oracle ok, computing next_event')
    nevent = next_event(event)
    print(f'[POLICY]\tLOG\t Computed next event: {nevent}')
    if nevent is None:
        return json.dumps(msg)
    if nevent is not None:
        if nevent == 'ask_webhook':
            msg = ask_webhook(msg)
            nevent = create_event(msg)
            answer = consume_event(nevent, msg)
            print(f'[POLICY]\tLOG\t Answer: {answer}')
            return answer

def load_json_post(msg):
    if type(msg) is not dict:
        try:
            msg = json.loads(msg)
        except:
            print('[POLICY]\tERR\t Cannot load message as json.')
    return msg

async def handle_post(request):
    msg = await request.json()
    msg = load_json_post(msg)
    event = create_event(msg)
    try:
        return web.Response(text=consume_event(event, msg))
    except:
        print('[POLICY]\tERR\t Error consuming event:')
        print(event)
    return web.Response(text="prova")

def main():
    app = web.Application()
    app.add_routes([web.post('/', handle_post)])
    web.run_app(app, port=8080)

if __name__ == '__main__':
    main()
