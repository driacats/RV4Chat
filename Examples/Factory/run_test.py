import requests, time, os, signal, json, shutil
import start_service as service

rasa_url = "http://0.0.0.0:5005/webhooks/rest/webhook"
dialogflow_url = "http://0.0.0.0:8084"

# conversation = ["I need help", "I earn 200 dollars per month", "We have 2 children", "saales", "stop", "I will kill me", "saales", "stop", "I will kill me", "I need help", "I will kill me"]
conversation = [s.rstrip() for s in open("test_input.txt", 'r').readlines()]

def test_conversation(url, i):
    print("-- Test Number:", i)
    for msg in conversation:
        print(f"[TEST]\tUSER\t {msg}")
        data = {'sender': 'user', 'message': msg}
        start_time = time.time() * 1000
        if url == rasa_url:
            answer = json.loads(requests.post(url, json=data).text)
        else:
            answer = json.loads(requests.post(url, json=json.dumps(data)).text)
        with open('time' + str(i) + ".txt", 'a') as f:
            f.write(str((time.time() * 1000) - start_time) + "\n")
        print(f"[TEST]\tBOT\t {answer}")

platforms = ['dialogflow']
# platforms = ['rasa','dialogflow']
# monitors = ['no-monitor', 'dummy-monitor']
monitors = ['no-monitor', 'dummy-monitor', 'real-monitor']
N = 1 

for platform in platforms:
    if not os.path.exists('Times/' + platform + '/'):
        os.makedirs('Times/' + platform + '/')
    for monitor in monitors:
        if os.path.exists('Times/' + platform + '/' + monitor + '/'):
            shutil.rmtree('Times/' + platform + '/' + monitor + '/')
        os.makedirs('Times/' + platform + '/' + monitor + '/')
        print("==== Testing", platform, monitor, "====")
        if (platform == 'rasa'):
            for i in range(N):
                pids = service.run_rasa(monitor)
                time.sleep(40)
                test_conversation(rasa_url, i)
                shutil.move('time' + str(i) + '.txt', 'Times/' + platform + '/' + monitor + '/')
                for pid in pids:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
        else:
            for i in range(N):
                pids = service.run_dialogflow(monitor)
                time.sleep(2)
                test_conversation(dialogflow_url, i)
                shutil.move('time' + str(i) + '.txt', 'Times/' + platform + '/' + monitor + '/')
                for pid in pids:
                    os.killpg(os.getpgid(pid), signal.SIGTERM)
        
        
