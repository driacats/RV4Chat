from aiohttp import web
import json, requests, argparse

def build_msg(msg):

    action = None
    intent_name = None
    parameters = {}
    if msg in ['Add a table', 'Add a robot in front on the left', 'Add a robot in front on the right', 'Add a table behind on the left', 'Add a robot behind on the right']:
        action = 'add_object'
        parameters['posX'] = ''
        for posx in ['left', 'right', 'center']:
            if posx in msg:
                parameters['posX'] = posx
        parameters['posY'] = ''
        for posy in ['front', 'behind', 'center']:
            if posy in msg:
                parameters['posY'] = posy
        for obj in ['table', 'box', 'robot']:
            if obj in msg:
                parameters['object'] = obj
        intent_name = 'add_object'
    elif msg == 'Add a box right of table1':
        action = 'add_rel_object'
        parameters['relPos'] = 'right of'
        parameters['relName'] = 'table1'
        parameters['object'] = 'box'
        intent_name = 'add_relative_object'
    elif msg in ['Remove box0', 'Remove robot1', 'Remove table1', 'Remove table2', 'Remove robot2', 'Remove robot3']:
        action = 'remove_object'
        for obj in ['box0', 'robot1', 'table1', 'table2', 'robot2', 'robot3']:
            if obj in msg:
                parameters['relname'] = obj
        intent_name = 'remove_object'


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
    print(f"[DIAG]\tLOG\t{data}")
    data = json.loads(data)
    msg = data["message"]
    webhook_msg = json.loads(build_msg(msg))
    print(f"[DIAG]\tLOG\t Message to Webhook: {webhook_msg}")
    answer = requests.post('http://localhost:' + port, json=webhook_msg)
    print(f"[DIAG]\tLOG\t Webhook answer: {answer.text}")
    return web.Response(text=answer.text)

def main():
    parser = argparse.ArgumentParser(prog="Dummy Dialogflow Tester", description="This program simulates a Dialogflow API.")
    parser.add_argument("-p", "--port", metavar="PORT", help="Port on which send messages", default="8080")
    args = parser.parse_args()

    app = web.Application()
    app.add_routes([web.post('/', lambda request: handle_post(request, args.port))])
    web.run_app(app, port=8084)

if __name__ == "__main__":
    main()
