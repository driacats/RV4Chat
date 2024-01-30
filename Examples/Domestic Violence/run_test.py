import requests

url = "http://0.0.0.0:5005/webhooks/rest/webhook"
msg = "I need help"

conversation = ["I need help", "I earn 200 dollars per month", "We have 2 children", "saales", "stop", "I will kill me", "saales", "stop", "I will kill me", "I need help", "I will kill me"]

for _ in range(20):
    for msg in conversation:
        print("[USER]", msg)
        data = {'sender': 'user', 'message': msg}
        answer = requests.post(url, json=data).text
        print("[BOT]", answer)