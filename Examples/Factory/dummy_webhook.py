from aiohttp import web
import json, argparse, asyncio, websockets, time

# The Factory class implements a factory CAD placeholder.
# It has four main functions:
#  - print_factory(): prints the factory situation;
#  - add_object(obj, h, v): adds an object of type obj in position h horizontally and v vertically
#  - add_relative_object(obj, relObj, relPos): adds an object of type obj in relPos with respect to relObj
#  - removeObj(obj): removes the object obj from the factory.
# An example of use is:
#   factory = Factory()
#   factory.add_object('table', 'right', 'front') # adds a table in front on the right
#   factory.add_relative_object('box', 'table1', 'right of') # adds a box right of table1
#   factory.remove_object('table1') # removes table1

class Factory():

    positions = [[' ', ' ', ' '], [' ', ' ', ' '], [' ', ' ', ' ']]
    objects = {}
    counter = {'table': 0, 'box': 0, 'robot': 0}
    
    # * Relative positions:
    # - 'behind|center+front'
    # - 'left,center.right'
    # Example:
    #      A|t.b+c
    # - Behind there is A
    # - On the right there is b
    # - In front there is c
    # - The main object is t
    # The output should be:
    #  +---+
    #  | A |
    #  | tb|
    #  | c |
    #  +---+

    def print_factory(self):
        # build the row line between cells
        row_line = ''
        for i in range(len(self.positions)):
            row_line += '+---'
        row_line += '+'

        # for each row
        for row in self.positions:
            # print the row line as first thing
            print(row_line)

            # For 3 times we check each cell:
            # 0. one for behind objects
            # 1. one for centered objects
            # 2. one for front objects
            for i in range(3):
                for column in row:
                    # intialize behind and front as bank spaces
                    behind = ' '
                    front = ' '
                    # Look for behind objects
                    if ('|' in column):
                        column = column.split('|')
                        behind = column[0]
                        column = column[1]
                    # Look for front objects
                    column = column.split('+')
                    obj = column[0]
                    if (len(column) > 1):
                        front = column[1]

                    print('|', end='')

                    # The first round is for behind objects
                    if (i == 0):
                        pos = behind
                    # The second round for centered objects
                    elif (i == 1):
                        pos = obj
                    # The third one for the front objects
                    elif (i == 2):
                        pos = front
                    
                    # Check if there are objects left or right
                    pos_left = ' '
                    pos_right = ' '
                    if (',' in pos):
                        pos = pos.split(',')
                        pos_left = pos[0]
                        pos = pos[1]
                    pos = pos.split('.')
                    if (len(pos) > 1):
                        pos_right = pos[1]
                    pos = pos[0]
                    print(pos_left + pos + pos_right, end='')
                print('|')

        print(row_line)
        print('\n', end='')

        # Print the legend
        for obj in self.objects:
            print(f'{obj}: {self.objects[obj]}')

    # The add_object function takes as arguments:
    # - obj: the object to add
    # - h: the horizontal position (left, center, right)
    # - v: the vertical position (behind, center, front)
    # It tries to add the object
    def add_object(self, obj, h, v):
        print('[WEBHOOK]\tLOG\t called add object')
        # Get the correct indeces for self.positions
        if (h == 'right'):
            h = 2
        elif (h == 'left'):
            h = 0
        else:
            h = 1
        if (v == 'behind'):
            v = 0
        elif (v == 'front'):
            v = 2
        else:
            v = 1
        # Add the object to the objects dictionary
        self.objects[obj[0]] = obj
        # If the position is already took return false
        if (self.positions[v][h] != ' '):
            print('[WEBHOOK]\tLOG\t position already took')
            return False
        # add in the correct position of the string (if there are already other objects)
        if not (len(self.positions[v][h]) == 1):
            if (',' in self.positions[v][h]):
                i = self.positions[v][h].index(',')
                i = i + 1
            elif ('.' in self.positions[v][h]):
                i = self.positions[v][h].index('.')
                i = i - 1
            elif ('|' in self.positions[v][h]):
                i = self.positions[v][h].index('|')
                i = i + 1
            elif ('+' in self.positions[v][h]):
                i = self.positions[v][h].index('+')
                i = i - 1
            self.positions[v][h] = self.positions[v][h][:i] + obj[0] + self.positions[v][h][i+1:]
        else:
            self.positions[v][h] = obj[0]

        # Increase the id counter
        self.counter[obj] += 1
        return True


    # The function remove_object takes as argument:
    # - obj: the name of the object to be removed
    def remove_object(self, obj):
        print('[WEBHOOK]\tLOG\t Called remove object')
        # We check each position
        for i, row in enumerate(self.positions):
            for j, column in enumerate(row):
                # If we find the object remove it and return true
                if (obj[0] in column):
                    self.positions[i][j] = column.replace(obj[0], ' ')
                    return True
        # If we exit the cycle no object has been found, return false
        return False

    # The function add_relative_object takes as argument:
    # - obj: the object to be added
    # - relObj: the object used as reference
    # - relPos: the position with respect to the relObj one
    def add_relative_object(self, obj, relObj, relPos):
        print('[WEBHOOK]\tLOG\t Called add relative object')
        # If the object is not in the objects dictionary exit
        if (relObj[0] not in self.objects):
            print('[WEBHOOK]\tLOG\t Reference object not found')
            return False
        # Otherwise look for the object position
        for i, row in enumerate(self.positions):
            for j, column in enumerate(row):
                if (relObj[0] in column):
                    # Add the new object to the objects dictionary
                    self.objects[obj[0]] = obj
                    # Adds the object in the position string correctly following the pattern at line 10
                    if (relPos == 'left of'):
                        if ('|' in column):
                            column = column.split('|')
                            self.positions[i][j] = f'{column[0]}|{obj[0]},{column[1]}'
                        else:
                            self.positions[i][j] = f'{obj[0]},{column}'
                    elif (relPos == 'right of'):
                        if ('+' in column):
                            column = column.split("+")
                            self.positions[i][j] = f'{column[0]}.{obj[0]}+{column[1]}'
                        else:
                            self.positions[i][j] = f'{column}.{obj[0]}'
                    elif (relPos == 'behind of'):
                        self.positions[i][j] = f'{obj[0]}|{column}'
                    elif (relPos == 'in front of'):
                        self.positions[i][j] = f'{column}+{obj[0]}'
        return True

async def handle_msg(msg, factory):
    message = json.loads(msg)
    print(f'[WEBHOOK]\tLOG\t Received {message}')

    if (message['intent'] == 'add_object'):
        if factory.add_object(message['entities']['object'], message['entities']['posX'], message['entities']['posY']):
            obj_name = message['entities']['object'] + str(factory.counter[message['entities']['object']])
            answer = f'Object added, you can refer to as {obj_name}'
            event = 'utter_add_object'
        else:
            answer = 'Error in adding object'
    if (message['intent'] == 'add_relative_object'):
        if (factory.add_relative_object(message['entities']['object'], message['entities']['relName'], message['entities']['relPos'])):
            obj_name = message['entities']['object'] + str(factory.counter[message['entities']['object']])
            answer = f'Object added, you can refer to as {obj_name}'
            event = 'utter_add_relative_object'
        else:
            answer = 'Error in adding object'
    if (message['intent'] == 'remove_object'):
        if (factory.remove_object(message['entities']['relname'])):
            answer = 'Object removed'
            event = 'utter_remove_object'
        else:
            answer = "Error in adding object"

    factory.print_factory()

    return (answer, event)

async def handle_post(request, factory):
    # answer = "{\"fulfillmentMessages\":[{\"text\":{\"text\":[\"MESSAGE\"]}}], \"bot_action\": \"EVENT\"}"
    # Load the json message
    data = await request.json()
    # Check if it is a valid Dialogflow message
    if ('queryResult' not in data):
        print('[WEBHOOK]\tERR\t Message not valid.')
        return

    # Build the message in the form
    # {intent: _, entities: {e1: _, e2: _, ...}}
    # for the handle_msg function
    request = {}
    queryResult = data['queryResult']
    intent = queryResult['intent']['displayName']
    entities = {}
    for entity in queryResult['parameters']:
        entities[entity] = queryResult['parameters'][entity]
    
    request['intent'] = intent
    request['entities'] = entities

    # Compute the answer and the bot event
    (final_answer, bot_event) = await handle_msg(json.dumps(request), factory)
    # Build the answer for Dialogflow
    # final_answer = answer.replace("MESSAGE", final_answer).replace("EVENT", bot_event).replace("TIMESTAMP", str(time.time()))
    answer = {}
    answer['fulfillmentMessages'] = [{'text': {'text': [final_answer]}}]
    answer['bot_action'] = bot_event
    if (bot_event in ['utter_add_object', 'utter_add_relative_object']):
        name = final_answer.split()[-1]
        answer['aux'] = {'name': name}

    # Send back the message to be displayed
    return web.Response(text=json.dumps(answer))

# The handle_ws function manages WebSocket connections
async def handle_ws(request, factory):

    # Create a server that waits for messages
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    # For each message received handle
    # the message and compute the answer
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            request = {}
            (final_answer, bot_event) = await handle_msg(msg.data, factory)
            await ws.send_str(final_answer)
            
    return ws

def main():
    parser = argparse.ArgumentParser(prog='Dummy WebHook Server', description='This program simulates a Factory CAD assistant service')
    parser.add_argument('-p', metavar='platform', help='Platform to be used for connections.', default='rasa')
    args = parser.parse_args()

    factory = Factory()

    if (args.p == 'dialogflow'):
        app = web.Application()
        app.add_routes([web.post('/', lambda request: handle_post(request, factory))])
        web.run_app(app, port=8082)

    if (args.p == 'rasa'):
        app = web.Application()
        app.add_routes([web.get('/', lambda request: handle_ws(request, factory))])
        web.run_app(app, port=8082)

if __name__ == '__main__':
    main()
