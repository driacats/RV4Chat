#! /bin/python
# Author: Andrea Gatti

import subprocess, argparse, os, time

kitty = 'kitty --hold 2>/dev/null sh -c'

dialogflow = 'dialogflow'
rasa = 'rasa'
platforms = [dialogflow, rasa]

no_monitor = 'no-monitor'
dummy_monitor = 'dummy-monitor'
real_monitor = 'real-monitor'
monitors = [no_monitor, dummy_monitor, real_monitor]

def print_welcome():
    print('============ Rv4Chat ============')
    print('Domestic Violence Chatbot Example')
    print('=================================')

def print_start(platform, monitor):
    print('\n============ Rv4Chat ============\n')
    print('     Service Started Correctly\n')
    print('       Platform:', platform)
    print('       Monitor:', monitor, '\n')
    print('=================================')

def choose_platform():
    while(True):
        print('Choose the platform you want to use:')
        print(' [1] Dialogflow')
        print(' [2] Rasa')
        
        choice_i = input('> ')
        try:
            choice_i = int(choice_i)
        except:
            print('Choice not valid, try again.')
            continue
        if (choice_i > len(platforms)):
            print('Choice not valid, try again.')
        else:
            return platforms[choice_i - 1]

def choose_monitor():
    while(True):
        print('Choose the platform you want to use:')
        print(' [1] Without Monitor')
        print(' [2] With a Dunny Monitor')
        print(' [3] With the Real Monitor')
        choice_i = input('> ')
        try:
            choice_i = int(choice_i)
        except:
            print('Choice not valid, try again.')
            continue
        if (choice_i > len(monitors)):
            print('Choice not valid, try again.')
        else:
            return monitors[choice_i - 1]

def launch_ngrok(port):
    return subprocess.Popen(f'{kitty} \'ngrok http {port}\'', shell=True, preexec_fn=os.setsid).pid

def launch_dummy_dialogflow(port):
    return subprocess.Popen(f'python dialogflow_local_tester.py -p {port}', shell=True, preexec_fn=os.setsid).pid

def launch_policy():
    return subprocess.Popen(f'python Dialogflow/new_policy.py', shell=True, preexec_fn=os.setsid).pid

def launch_sample_monitor():
    return subprocess.Popen(f'{kitty} \'python ../../sample_monitor_ws.py\'', shell=True, preexec_fn=os.setsid).pid

def launch_monitor():
    return subprocess.Popen(f'Monitor/online_monitor.sh Monitor/Properties/suicide_identification.pl 5052', shell=True, preexec_fn=os.setsid).pid

def launch_webhook(platform):
    return subprocess.Popen(f'{kitty} \'python dummy_webhook.py -p {platform}\'', shell=True, preexec_fn=os.setsid).pid

def run_dialogflow(monitor):
    pids = []

    if (monitor == no_monitor):
        pid = launch_dummy_dialogflow(8082)
        pids.append(pid)
        pid = launch_webhook('dialogflow')
        pids.append(pid)

    elif (monitor == dummy_monitor):
        pid = launch_webhook('dialogflow')
        pids.append(pid)
        pid = launch_dummy_dialogflow(8080)
        pids.append(pid)
        pid = launch_sample_monitor()
        pids.append(pid)
        time.sleep(1)
        pid = launch_policy()
        pids.append(pid)

    elif (monitor == real_monitor):
        pid = launch_webhook('dialogflow')
        pids.append(pid)
        pid = launch_dummy_dialogflow(8080)
        pids.append(pid)
        pid = launch_monitor()
        pids.append(pid)
        time.sleep(1)
        pid = launch_policy()
        pids.append(pid)

    return pids

def run_rasa(monitor):

    pids = []

    rasa_command = 'rasa run -m models/model-no-policy.tar.gz'
    
    if (monitor == dummy_monitor):
        pid = launch_sample_monitor()
        pids.append(pid)
        rasa_command = 'rasa run -m models/model-with-policy.tar.gz'
        
    elif (monitor == real_monitor):
        pid = launch_monitor()
        pids.append(pid)
        rasa_command = 'rasa run -m models/model-with-policy.tar.gz'

    pid = launch_webhook('rasa')
    pids.append(pid)

    pid = subprocess.Popen(f'{kitty} \'cd Rasa && source .venv/bin/activate && {rasa_command}\'', shell=True, preexec_fn=os.setsid).pid
    pids.append(pid)
    pid = subprocess.Popen(f'{kitty} \'cd Rasa && source .venv/bin/activate && rasa run actions\'', shell=True, preexec_fn=os.setsid).pid
    pids.append(pid)

    return pids

def main():

    parser = argparse.ArgumentParser(prog='Dummy WebHook Server', description='This program simulates a Domestic Violence assistant service')
    parser.add_argument('-s', '--shell', action='store_true', help='launch the script with arguments.')
    parser.add_argument('-p', '--platform', metavar='chatbot', help='platform to be used for connections. Platforms available: rasa, dialogflow')
    parser.add_argument('-m', '--monitor', metavar='monitor', help='monitor to be used. Monitors available: no-monitor, dummy-monitor, real-monitor')
    args = parser.parse_args()

    if (args.shell):
        if not (args.platform and args.monitor):
            parser.error('If the shell mode is enabled the platform and the monitor must be specified.')
        platform = args.platform
        monitor = args.monitor

    else:
        print_welcome()
        platform = choose_platform()
        monitor = choose_monitor()

    if (platform == dialogflow):
        run_dialogflow(monitor)
    elif (platform == rasa):
        run_rasa(monitor)

    if (not args.shell):
        print_start(platform, monitor)

if (__name__ == '__main__'):
    main()
