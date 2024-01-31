import subprocess

dialogflow = 'dialogflow'
rasa = 'rasa'

no_monitor = 'no-monitor'
dummy_monitor = 'dummy-monitor'
real_monitor = 'real-monitor'

def print_welcome():
    print("============ Rv4Chat ============")
    print("Domestic Violence Chatbot Example")
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
    subprocess.Popen(f"kitty --hold ngrok http {port}", shell=True)

def launch_sample_monitor():
    subprocess.Popen(f"kitty --hold python ../../sample_monitor_ws.py", shell=True)

def launch_monitor():
    print("Not available")
    # subprocess.Popen(f"kitty --hold Monitor/online_monitor.sh", shell=True)

def launch_webhook(platform):
    subprocess.Popen(f"kitty --hold python dummy_webhook.py -p {platform}", shell=True)

def run_dialogflow(monitor):
    if (monitor == no_monitor):
        print("ngrok http 8082")
        launch_ngrok(8082)

    elif (monitor == dummy_monitor):
        print("ngrok http 8080")
        launch_ngrok(8080)
        print("../../sample_monitor_ws.py")
        launch_sample_monitor()

    elif (monitor == real_monitor):
        print("ngrok http 8080")
        launch_ngrok(8080)
        print("Monitor/online_monitor.sh")
        launch_monitor()

    print("dummy_webhook.py - p dialogflow")
    launch_webhook("dialogflow")

def run_rasa(monitor):
    
    if (monitor == dummy_monitor):
        print("../../sample_monitor_ws.py")
        launch_sample_monitor()
        
    elif (monitor == real_monitor):
        print("Monitor/online_monitor.sh")
        launch_monitor()

    print("dummy_webhook.py - p rasa")
    launch_webhook("rasa")

    subprocess.Popen(f"kitty --hold bash -c 'cd Rasa && source .venv/bin/activate && rasa run'", shell=True)
    subprocess.Popen(f"kitty --hold bash -c 'cd Rasa && source .venv/bin/activate && rasa run actions'", shell=True)

def main():
    print_welcome()
    platform = choose_platform()
    monitor = choose_monitor()

    print(platform, monitor)

    if (platform == dialogflow):
        run_dialogflow(monitor)
    elif (platform == rasa):
        run_rasa(monitor)

if __name__ == "__main__":
    main()