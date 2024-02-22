import requests, time, os, signal, json, shutil, argparse, subprocess, psutil
import start_service as service

rasa_url = 'http://0.0.0.0:5005/webhooks/rest/webhook'
dialogflow_url = 'http://0.0.0.0:8084'

conversation = [s.rstrip() for s in open('test_input.txt', 'r').readlines()]

def test_conversation(url, i):
    print('-- Test Number:', i)
    for msg in conversation:
        print(f'[TESTING]\tUSER\t {msg}')
        data = {'sender': 'user', 'message': msg}
        start_time = time.time() * 1000
        if url == rasa_url:
            answer = json.loads(requests.post(url, json=data).text)
        else:
            answer = json.loads(requests.post(url, json=json.dumps(data)).text)
        with open('time' + str(i) + '.txt', 'a') as f:
            f.write(str((time.time() * 1000) - start_time) + '\n')
        print(f'[TESTING]\tBOT\t {answer}')

def interactive(url):
    print('===== Factory CAD Test Interactive =====')
    while(True):
        msg = input('\033[1;36;40m> ')
        print('\033[0m')
        if msg == 'exit':
            print('\033[1;34;40mBOT: Goodbye!')
            return
        data = {'sender': 'user', 'message': msg}
        if url == rasa_url:
            answer = json.loads(requests.post(url, json=data).text)
            answer = answer[0]['text']
        else:
            answer = json.loads(requests.post(url, json=json.dumps(data)).text)
            answer = answer['fulfillmentMessages'][0]['text']['text'][0]
        print('\033[1;34;40mBOT:', answer, '\033[0m')

def launch_interactive(args):
    if not args.platform or not args.monitor:
        print('You have to specify the platform and the monitor.')
        return
    print('Launching Service...')
    if args.platform == 'rasa':
        # pids = service.run_rasa(args.monitor)
        terminal = subprocess.Popen('kitty --hold 2>/dev/null sh -c \'python start_service.py -s -p rasa -m ' + args.monitor + '\'', shell=True, preexec_fn=os.setsid)
        time.sleep(40)
        interactive(rasa_url)
    elif args.platform == 'dialogflow':
        terminal = subprocess.Popen('kitty --hold 2>/dev/null sh -c \'python start_service.py -s -p dialogflow -m ' + args.monitor + '\'', shell=True, preexec_fn=os.setsid)
        # pids = service.run_dialogflow(args.monitor)
        time.sleep(2)
        interactive(dialogflow_url)
    else:
        print('Monitor specified not known.')
    parent = psutil.Process(terminal.pid)
    for child in parent.children(recursive=True):
        child.kill()
    terminal.kill()
    # os.killpg(os.getpgid(pid), signal.SIGTERM)

def launch_tests():
    platforms = ['dialogflow']
    # platforms = ['rasa','dialogflow']
    # platforms = ['rasa']
    # monitors = ['no-monitor', 'dummy-monitor']
    monitors = ['no-monitor', 'dummy-monitor', 'real-monitor']
    # monitors = ['real-monitor']
    N = 1

    for platform in platforms:
        if not os.path.exists('Times/' + platform + '/'):
            os.makedirs('Times/' + platform + '/')
        for monitor in monitors:
            if os.path.exists('Times/' + platform + '/' + monitor + '/'):
                shutil.rmtree('Times/' + platform + '/' + monitor + '/')
            os.makedirs('Times/' + platform + '/' + monitor + '/')
            print('==== Testing', platform, monitor, '====')
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

def main():
    parser = argparse.ArgumentParser(prog='Test Case Runner', description='A fully running tester for the Factory CAD domain.')
    parser.add_argument('-i', '--interactive', action='store_true', help='launch the script in interactive mode.')
    parser.add_argument('-p', '--platform', metavar='chatbot', help='platform to be used as backend.Platforms available: rasa, dialogflow')
    parser.add_argument('-m', '--monitor', metavar='monitor', help='monitor to be used. Monitors available: no-monitor, dummy-monitor, real-monitor')
    args = parser.parse_args()

    if args.interactive:
        launch_interactive(args)
    else:
        launch_tests()

if __name__ == '__main__':
    main()
