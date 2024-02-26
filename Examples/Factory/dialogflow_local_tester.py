#! /bin/python
#  Author: Andrea Gatti

from aiohttp import web
import json, requests, argparse, re

# The function builds the Dialogflow JSON message
# with default values.
def build_msg(msg):

    action = None
    intent_name = None
    parameters = {}

    # Catches removal messages
    if ('Remove' in msg):
        intent_name = 'remove_object'
        action = 'remove_object'
        obj = msg.split()[-1]
        parameters['relname'] = obj
    else:
        # Referenced Addition
        if ('of' in msg):
            intent_name = 'add_relative_object'
            action = 'add_relative_object'
            pattern = r'Add a (\w+) (right of|left of|behind of|in front of) (\w+)'
            match = re.match(pattern, msg)
            if (match):
                parameters['object'] = match.group(1)
                parameters['relName'] = match.group(3)
                parameters['relPos'] = match.group(2)
        else:
            # Global addition
            intent_name = 'add_object'
            action = 'add_object'
            pattern = r'Add a (\w+) ?(:?in )?(behind|front)? ?(:?on the )?(left|right)?'
            match = re.match(pattern, msg)
            print(f'[DIALOG]\tLOG\tmatch[1] {match.group(1)} match[2] {match.group(3)} match[3] {match.group(5)}')
            if (match):
                if (match.group(1)):
                    parameters['object'] = match.group(1)
                if (match.group(5)):
                    parameters['posX'] = match.group(5)
                else:
                    parameters['posX'] = ''
                if (match.group(3)):
                    parameters['posY'] = match.group(3)
                else:
                    parameters['posY'] = ''

    print(f'[DIALOG]\tLOG\tFound in message. Intent: {intent_name}, Entities: {parameters}')

    # Build the Dictionary answer
    answer = {}
    answer['responseId'] = 'XXXX'
    
    queryResult = {}
    queryResult['queryText'] = msg
    queryResult['action'] = action
    queryResult['parameters'] = parameters
    queryResult['allRequiredParamsPresent'] = True
    queryResult['fulfillmentText'] = 'No answer from the server'
    
    text_list = ['No answer from the server.']
    text = {}
    text['text'] = text_list
    fulfillmentMessages = [{'text': text}]
    queryResult['fulfillmentMessages'] = fulfillmentMessages
    
    intent = {}
    intent['name'] = 'XXXX'
    intent['displayName'] = intent_name
    queryResult['intent'] = intent
    queryResult['intentDetectionConfidence'] = 1
    
    latency = {}
    latency['webhook_latency_ms'] = 100
    queryResult['diagnosticInfo'] = latency
    
    queryResult['languageCode'] = 'en'
    queryResult['sentimentAnalysisResult'] = {'queryTextSentiment': {}}
    answer['queryResult'] = queryResult
    answer['agentId'] = 'XXXX'
    
    # Return the JSON string emulating Dialogflow
    return json.dumps(answer)


async def handle_post(request, port):

    data = await request.json()
    print(f'[DIALOG]\tLOG\t{data}')
    if type(data) is not dict:
        data = json.loads(data)
    
    # Retrieve the user message text
    msg = data['message']
    # Build the Dialogflow JSON estracted information
    webhook_msg = json.loads(build_msg(msg))
    print(f'[DIALOG]\tLOG\t Message to Webhook: {webhook_msg}')
    # Send the message to the WebHook
    answer = requests.post(f'http://localhost:{port}', json=webhook_msg)
    print(f'[DIALOG]\tLOG\t Webhook answer: {answer.text}')
    # Answer with the returned message
    return web.Response(text=answer.text)

def main():
    parser = argparse.ArgumentParser(prog='Dummy Dialogflow Tester', description='This program simulates a Dialogflow API.')
    parser.add_argument('-p', '--port', metavar='PORT', help='Port on which send messages', default=8080)
    args = parser.parse_args()

    app = web.Application()
    app.add_routes([web.post('/', lambda request: handle_post(request, args.port))])
    web.run_app(app, port=8084)

if __name__ == '__main__':
    main()
