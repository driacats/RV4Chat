from http.server import BaseHTTPRequestHandler, HTTPServer
import json, requests

class FactoryWebHook(BaseHTTPRequestHandler):

    answer = "{\"fulfillmentMessages\":[{\"text\":{\"text\":[\"MESSAGE\"]}}], \"bot_action\": \"EVENT\", \"aux\": {AUX}}"
    positions = [[" ", " ", " "], [" ", " ", " "], [" ", " ", " "]]
    objects = {}
    counter = {"table": 0, "box": 0, "robot": 0}
    # Relative positions:
    # - "behind|center+front"
    # - "left,center.right"
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
        row_line = ""
        for i in range(len(self.positions)):
            row_line += "+---"
        row_line += "+"

        # for each row
        for row in self.positions:
            # print the row line as first thing
            print(row_line)

            # For 3 times we check each cell:
            # i. 
            # 0. one for behind objects
            # 1. one for centered objects
            # 2. one for front objects
            for i in range(3):
                for column in row:
                    # intialize behind and front as bank spaces
                    behind = " "
                    front = " "
                    # Look for behind objects
                    if "|" in column:
                        column = column.split("|")
                        behind = column[0]
                        column = column[1]
                    # Look for front objects
                    column = column.split("+")
                    obj = column[0]
                    if len(column) > 1:
                        front = column[1]

                    print("|", end="")

                    # The first round is for behind objects
                    if i == 0:
                        pos = behind
                    # The second round for centered objects
                    elif i == 1:
                        pos = obj
                    # The third one for the front objects
                    elif i == 2:
                        pos = front
                    
                    # Check if there are objects left or right
                    pos_left = " "
                    pos_right = " "
                    if "," in pos:
                        pos = pos.split(",")
                        pos_left = pos[0]
                        pos = pos[1]
                    pos = pos.split(".")
                    if len(pos) > 1:
                        pos_right = pos[1]
                    pos = pos[0]
                    print(pos_left + pos + pos_right, end="")
                print("|")

        print(row_line)
        print("\n", end="")

        # Print the legend
        for obj in self.objects:
            print(obj, ":", self.objects[obj])

    # The add_object function takes as arguments:
    # - obj: the object to add
    # - h: the horizontal position (left, center, right)
    # - v: the vertical position (behind, center, front)
    # It tries to add the object
    def add_object(self, obj, h, v):
        print("[LOG] called add object")
        # Get the correct indeces for self.positions
        if h == "right":
            h = 2
        elif h == "left":
            h = 0
        else:
            h = 1
        if v == "behind":
            v = 0
        elif v == "front":
            v = 2
        else:
            v = 1
        # Add the object to the objects dictionary
        self.objects[obj[0]] = obj
        # If the position is already took return false
        if self.positions[v][h] != " ":
            print("[LOG] position already took")
            return False
        # add in the correct position of the string (if there are already other objects)
        if not len(self.positions[v][h]) == 1:
            if "," in self.positions[v][h]:
                i = self.positions[v][h].index(",")
                i = i + 1
            elif "." in self.positions[v][h]:
                i = self.positions[v][h].index(".")
                i = i - 1
            elif "|" in self.positions[v][h]:
                i = self.positions[v][h].index("|")
                i = i + 1
            elif "+" in self.positions[v][h]:
                i = self.positions[v][h].index("+")
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
        print("[LOG] called remove object")
        # We check each position
        for i, row in enumerate(self.positions):
            for j, column in enumerate(row):
                # If we find the object remove it and return true
                if obj[0] in column:
                    self.positions[i][j] = column.replace(obj[0], " ")
                    return True
        # If we exit the cycle no object has been found, return false
        return False

    # The function add_relative_object takes as argument:
    # - obj: the object to be added
    # - relObj: the object used as reference
    # - relPos: the position with respect to the relObj one
    def add_relative_object(self, obj, relObj, relPos):
        print("[LOG] called add relative object")
        # If the object is not in the objects dictionary exit
        if relObj[0] not in self.objects:
            print("[LOG] Reference object not found")
            return False
        # Otherwise look for the object position
        for i, row in enumerate(self.positions):
            for j, column in enumerate(row):
                if relObj[0] in column:
                    # Add the new object to the objects dictionary
                    self.objects[obj[0]] = obj
                    # Adds the object in the position string correctly following the pattern at line 10
                    if relPos == "left of":
                        if "|" in column:
                            column = column.split("|")
                            self.positions[i][j] = column[0] + "|" + obj[0] + "," + column[1]
                        else:
                            self.positions[i][j] = obj[0] + "," + column
                    elif relPos == "right of":
                        if "+" in column:
                            column = column.split("+")
                            self.positions[i][j] = column[0] + "." + obj[0] + "+" + column[1] 
                        else:
                            self.positions[i][j] = column + "." + obj[0]
                    elif relPos == "behind of":
                        self.positions[i][j] = obj[0] + "|" + column
                    elif relPos == "in front of":
                        self.positions[i][j] = column + "+" + obj[0]
        return True

    def do_POST(self):

        # Accept the request
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        message = json.loads(post_data)
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

        if not "queryResult" in message:
             print("[LOG] Message not valid.")
             return

        # Get intent and entities from the request
        intent = message["queryResult"]["intent"]["displayName"]
        entities = {}
        for entity in message["queryResult"]["parameters"]:
            entities[entity] = message["queryResult"]["parameters"][entity]

        # Add object intent
        if intent == "add_object":
            if self.add_object(entities["Object"], entities["posX"], entities["posY"]):
                obj_name = entities["Object"] + str(self.counter[entities["Object"]])
                answer = self.answer.replace("MESSAGE", "Object added correctly! You can refer to it as " + obj_name)
                answer = answer.replace("EVENT", "utter_add_object")
                answer = answer.replace("AUX", "\"name\": \"" + obj_name + "\"")
            else:
                answer = self.answer.replace("MESSAGE", "Error adding object.")
                answer = answer.replace("EVENT", "utter_object_not_added")
                answer = answer.replace(", \"aux\": {AUX}", "")

        # Remove object intent
        elif intent == "remove_object":
            if self.remove_object(entities["relname"]):
                answer = self.answer.replace("MESSAGE", "Object removed correctly!")
                answer = answer.replace("EVENT", "utter_remove_object")
                answer = answer.replace(", \"aux\": {AUX}", "")
            else:
                answer = self.answer.replace("MESSAGE", "Error removing object.")
                answer = answer.replace("EVENT", "object_not_removed")
                answer = answer.replace(", \"aux\": {AUX}", "")
        
        # Add relative object
        elif intent == "add_relative_object":
            if self.add_relative_object(entities["Object"], entities["relName"], entities["relPos"]):
                obj_name = entities["Object"] + str(self.counter[entities["Object"]])
                answer = self.answer.replace("MESSAGE", "Object added correctly! You can refer to it as " + obj_name)
                answer = answer.replace("EVENT", "utter_add_relative_object")
                answer = answer.replace("AUX", "\"name\": \"" + obj_name + "\"")
            else:
                answer = self.answer.replace("MESSAGE", "Error adding object.")
                answer = answer.replace("EVENT", "utter_object_not_added")
                answer = answer.replace(", \"aux\": {AUX}", "")

        # Error
        else:
            answer = self.answer.replace("MESSAGE", "Unknown error.")
            answer = answer.replace("EVENT", "error")

        # Send the answer
        self.wfile.write(bytes(answer, 'utf8'))
        # Print the factory
        self.print_factory()

def run(PORT):
    print("Server launch...")
    httpd = HTTPServer(("localhost", PORT), FactoryWebHook)
    httpd.serve_forever()

run(8082)
