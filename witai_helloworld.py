import requests, json

def send_message(message):
    headers = {
        'Authorization': 'Bearer PGCLOLWKU6NNY25KR54FT7PQVOJQX73D',
    }

    params = {
        'v': '20231010',
        'q': message,
    }

    return json.loads(requests.get('https://api.wit.ai/message', params=params, headers=headers).content)


while(True):
    message = input("> ")
    answer = send_message(message)
    print(answer["traits"]["Hello"][0]["value"])
