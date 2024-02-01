import subprocess, argparse

kitty = "kitty --hold 2>/dev/null sh -c"

dialogflow = 'dialogflow'
rasa = 'rasa'

no_monitor = 'no-monitor'
dummy_monitor = 'dummy-monitor'
real_monitor = 'real-monitor'

def print_welcome():
    print("============ Rv4Chat ============")
    print("     Factory Chatbot Example")
    print("=================================")

def print_start(platform, monitor):
    print("\n============ Rv4Chat ============\n")
    print("     Service Started Correctly\n")
    print("       Platform:", platform)
    print("       Monitor:", monitor, "\n")
    print("=================================")

def choose_platform():
    while(True):
        print("Choose the platform you want to use:")
        print(" [1] Dialogflow")
        print(" [2] Rasa")
        choice_i = input("> ")
        try:
            choice_i = int(choice_i)
        except:
            print("Choice not valid, try again.")
            continue
        if choice_i == 1:
            return dialogflow
        elif choice_i == 2:
            return rasa
        else:
            print("Choice not valid, try again.")

def choose_monitor():
    while(True):
        print("Choose the platform you want to use:")
        print(" [1] Without Monitor")
        print(" [2] With a Dunny Monitor")
        print(" [3] With the Real Monitor")
        choice_i = input("> ")
        try:
            choice_i = int(choice_i)
        except:
            print("Choice not valid, try again.")
            continue
        if choice_i == 1:
            return no_monitor
        elif choice_i == 2:
            return dummy_monitor
        elif choice_i == 3:
            return real_monitor
        else:
            print("Choice not valid, try again.")

def launch_ngrok(port):
    subprocess.Popen(f"{kitty} 'ngrok http {port}'", shell=True)

def launch_sample_monitor():
    subprocess.Popen(f"{kitty} 'python ../../sample_monitor_ws.py'", shell=True)

def launch_monitor():
    print("Not available")
    # subprocess.Popen(f"kitty --hold Monitor/online_monitor.sh", shell=True)

def launch_webhook(platform):
    subprocess.Popen(f"{kitty} 'python dummy_webhook.py -p {platform}'", shell=True)

def run_dialogflow(monitor):
    if (monitor == no_monitor):
        launch_ngrok(8082)

    elif (monitor == dummy_monitor):
        launch_ngrok(8080)
        launch_sample_monitor()

    elif (monitor == real_monitor):
        launch_ngrok(8080)
        launch_monitor()

    launch_webhook("dialogflow")

def run_rasa(monitor):
    
    if (monitor == dummy_monitor):
        launch_sample_monitor()
        
    elif (monitor == real_monitor):
        launch_monitor()

    launch_webhook("rasa")

    subprocess.Popen(f"{kitty} 'cd Rasa && source .venv/bin/activate && rasa run'", shell=True)
    subprocess.Popen(f"{kitty} 'cd Rasa && source .venv/bin/activate && rasa run actions'", shell=True)

def main():

    parser = argparse.ArgumentParser(prog="Dummy WebHook Server", description="This program simulates a Domestic Violence assistant service")
    parser.add_argument('-s', '--shell', action='store_true', help='launch the script with arguments.')
    parser.add_argument('-p', '--platform', metavar="chatbot", help="platform to be used for connections. Platforms available: rasa, dialogflow")
    parser.add_argument('-m', '--monitor', metavar="monitor", help="monitor to be used. Monitors available: no-monitor, dummy-monitor, real-monitor")
    args = parser.parse_args()

    if (args.shell):
        if not (args.platform and args.monitor):
            parser.error("If the shell mode is enabled the platform and the monitor must be specified.")
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

    if not args.shell:
        print_start(platform, monitor)

if __name__ == "__main__":
    main()