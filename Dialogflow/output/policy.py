# File generated automatically on 2024-02-26 17:28 by instrumenter.py
#  - Agent: DomesticViolenceHelper
#  - Input zip: ../Examples/Domestic Violence/Dialogflow/DomesticViolenceHelper.zip
#  - Output zip: output/DomesticViolenceHelperMonitored.zip
#  - WebHook URL: https://163e-130-251-61-251.ngrok-free.app
#  - Monitor URL: ws://localhost:5052
#  - Monitoring Level: 2


from aiohttp import web
from websocket import create_connection
import urllib3, json, random

MONITOR_URL = "ws://localhost:5052"
WEBHOOK_URL = "http://localhost:8082"

webhook = urllib3.PoolManager()

# Create User Event takes a Dialogflow message
# and creates the corresponding event.
# A user event has this format:
#   sender: user, 
#   receiver:bot, 
#   intent: {name: _, confidence: _}
#   entities: {e1: _, e2: _, ..., eN: _}
# The function returns a dict.
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
        print(f'[POLICY]\tLOG\t entity {entity} has value \"{queryResult["parameters"][entity]}\"')
        entities[entity] = queryResult['parameters'][entity]

    event['entities'] = entities

    print(f'[POLICY]\tLOG\t Event generated: {event}')

    return event

def create_bot_event(msg):
    # In the case of bot event the msg comes from the bot
    # and not from Dialogflow. In this case we assume that
    # the message is already formatted in a monitorizable way
    # and that we have only to add sender, receiver and event if needed.
    # Other parameters can change a lot depending on the action.
    event = msg
    if ('sender' not in event):
        event['sender'] = 'bot'
    if ('receiver' not in event):
        event['receiver'] = 'user'
    if ('bot_action' not in event):
        event['bot_action'] = 'unknown_event'

    return event

def create_event(msg):
    if ('queryResult' in msg):
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

def choose_answer(msg):
	if msg['queryResult']['intent']['displayName'] == 'Default Welcome Intent':
		return input_welcome()
	if msg['queryResult']['intent']['displayName'] == 'Default Fallback Intent':
		return input_unknown()


def input_welcome():
	available_answers = ['Hi! How are you doing?', 'Hello! How can I help you?', 'Good day! What can I do for you today?', 'Greetings! How can I assist?']
	msg = {}
	msg['fulfillmentMessages'] = [{'text': {'text': [random.choice(available_answers)]}}]
	return msg

def input_unknown():
	available_answers = ["I didn't get that. Can you say it again?", 'I missed what you said. What was that?', 'Sorry, could you say that again?', 'Sorry, can you say that again?', 'Can you say that again?', "Sorry, I didn't get that. Can you rephrase?", 'Sorry, what was that?', 'One more time?', 'What was that?', 'Say that one more time?', "I didn't get that. Can you repeat?", 'I missed that, say that again?']
	msg = {}
	msg['fulfillmentMessages'] = [{'text': {'text': [random.choice(available_answers)]}}]
	return msg


# If the event is a bot event it returns None.
# ask_webhhok if needed, plain_answer else.
def next_event(event):
    if (event['sender'] == 'bot'):
        return None
    if (event['intent']['name'] in ['inform_chatbot_about_salary', 'commit_suicide', 'inform_chatbot_about_children', 'undo_word', 'get_information', 'help_word']):
        return 'ask_webhook'
    return 'plain_answer'

# Given an event the consume_event passes it to the monitor.
# If the monitor returns True it computes the next event to be performed
# If the next event is None it is the final action -> answer returned.
# If the next event is ask_webhook it asks the webhook an answer.
# If the next event is plain_answer it returns the correct one.
def consume_event(event, msg):
    oracle = ask_monitor(event)
    if (not oracle):
        raise RuntimeError('[POLICY]\tERR\t Error raised by the monitor.')
    nevent = next_event(event)
    print(f'[POLICY]\tLOG\t Computed next event: {nevent}')
    if (nevent is None):
        return json.dumps(msg)
    if (nevent == 'ask_webhook'):
        msg = ask_webhook(msg)
        nevent = create_event(msg)
        answer = consume_event(nevent, msg)
        print(f'[POLICY]\tLOG\t Answer: {answer}')
        return answer
    if (nevent == 'plain_answer'):
        msg = choose_answer(msg)
        nevent = create_event(msg)
        answer = consume_event(nevent, msg)
        return answer

# A function that simply returns a dict from a JSON message
# if not already correctly loaded.
def load_json_post(msg):
    if (type(msg) is not dict):
        try:
            msg = json.loads(msg)
        except:
            print('[POLICY]\tERR\t Cannot load message as json.')
    return msg

# When a POST request arrives it is handled by the handle_post.
# The message is loaded in a dict from the load_json_post,
# An event is created from the create_event and passed to the
# consume_event. The consume event will return the response.
async def handle_post(request):
    msg = await request.json()
    msg = load_json_post(msg)
    event = create_event(msg)
    try:
        return web.Response(text=consume_event(event, msg))
    except:
        print('[POLICY]\tERR\t Error consuming event:')
        print(event)
        return web.Response(text="{\"answer\": \"Error thrown by the monitor.\"}")

def main():

    app = web.Application()
    app.add_routes([web.post('/', handle_post)])
    web.run_app(app, port=8080)

if (__name__ == '__main__'):
    main()
