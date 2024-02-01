import requests, time, os, signal, json, shutil
import start_service as service

rasa_url = "http://0.0.0.0:5005/webhooks/rest/webhook"

# conversation = ["I need help", "I earn 200 dollars per month", "We have 2 children", "saales", "stop", "I will kill me", "saales", "stop", "I will kill me", "I need help", "I will kill me"]
conversation = [s.rstrip() for s in open("test_input.txt", 'r').readlines()]

def test_conversation(url, i):
    print("-- Test Number:", i)
    for msg in conversation:
        print("[USER]", msg)
        data = {'sender': 'user', 'message': msg}
        start_time = time.time() * 1000
        answer = json.loads(requests.post(url, json=data).text)
        with open('time' + str(i) + ".txt", 'a') as f:
            f.write(str((time.time() * 1000) - start_time) + "\n")
        print("[BOT]", answer[0]['text'])

platforms = ['rasa']
monitors = ['no-monitor', 'dummy-monitor']

for platform in platforms:
    if not os.path.exists('Times/' + platform + '/'):
        os.makedirs('Times/' + platform + '/')
    for monitor in monitors:
        if os.path.exists('Times/' + platform + '/' + monitor + '/'):
            shutil.rmtree('Times/' + platform + '/' + monitor + '/')
        os.makedirs('Times/' + platform + '/' + monitor + '/')
        print("==== Testing", platform, monitor, "====")
        if (platform == 'rasa'):
            pids = service.run_rasa(monitor)
            time.sleep(45)
            for i in range(100):
                test_conversation(rasa_url, i)
                shutil.move('time' + str(i) + '.txt', 'Times/' + platform + '/' + monitor + '/')
            for pid in pids:
                os.killpg(os.getpgid(pid), signal.SIGTERM)
        else:
            pids = service.run_dialogflow(monitor)
        
        
