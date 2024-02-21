from aiohttp import web
import json, requests, argparse, re

def build_msg(msg):

    action = None
    intent_name = None
    parameters = {}

    if (msg == 'I need help'):
        intent_name = 'get_information'
    elif (msg == 'I earn 200 dollars per month'):
        intent_name = 'inform_chatbot_about_salary'
    elif (msg == 'We have 2 children'):
        intent_name = 'inform_chatbot_about_children'
    elif (msg == 'saales'):
        intent_name = 'help_word'
    elif (msg == 'stop'):
        intent_name = 'undo_word'
    elif (msg == 'help_called'):
        intent_name = 'help_called'
    elif (msg == 'I will kill me'):
        intent_name = 'commit_suicide'

    print(f'[DIALOG]\tLOG\tFound in message. Intent:{intent_name}, Entities:{parameters}')

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
    return json.dumps(answer)


async def handle_post(request, port):

    data = await request.json()
    print(f"[DIALOG]\tLOG\t{data}")
    if type(data) != dict:
        data = json.loads(data)

    # if (data['sender'] == 'bot'):
    #     m = {'sender': 'bot', 'msg': data['message']}
    #     requests.post('http://localhost:8888', json=m)
    #     return web.Response(status=200)
    msg = data["message"]
    if (data['sender'] == 'user'):
        webhook_msg = json.loads(build_msg(msg))
        print(f"[DIALOG]\tLOG\t Message to Webhook: {webhook_msg}")
        answer = requests.post('http://localhost:' + port, json=webhook_msg)
        print(f"[DIALOG]\tLOG\t Message got: {answer.text}")
        print(f"[DIALOG]\tLOG\t Webhook answer: {answer.text}")
        return web.Response(text=answer.text)
    if (data['message'] == 'help_called'):
        m = {'sender': 'bot', 'msg': 'The sun shines today!'}
        requests.post('http://localhost:8888', json=m)
        return web.Response(status=200)

def main():
    parser = argparse.ArgumentParser(prog="Dummy Dialogflow Tester", description="This program simulates a Dialogflow API.")
    parser.add_argument("-p", "--port", metavar="PORT", help="Port on which send messages", default=8080)
    args = parser.parse_args()

    app = web.Application()
    app.add_routes([web.post('/', lambda request: handle_post(request, args.port))])
    web.run_app(app, port=8084)

if __name__ == "__main__":
    main()
