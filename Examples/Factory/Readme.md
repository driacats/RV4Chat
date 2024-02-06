### Factory CAD Example

This chatbot helps a non expert user to place robots inside a factory in order to find the best and safest configuration.
In this example you can find the Dialogflow agent and a dummy monitor that simulates the execution of the CAD virtual system sending right messages back to the chat and taking into account the execution.

The user can perform three actions:
 - add a robot with the global reference frame;
 - add a robot with position related to one of the objects already placed;
 - remove a robot from the factory.

In this folder you find:
- A script that starts all the services needed to test one specific platform and monitor (`start_service.py`). If you launch it with no argument it will ask you what you want to run. Otherwise you can launch it in `--shell` mode giving it directly platform and monitor. Once launched the service will wait for messages to come via POST requests.
- A script that enables the user to perform tests (`run_test.py`). You can launch it in two ways:
  1. Interactive (`--interactive`): you specify platform and monitor and chat on the terminal.
  2. Test: run the tests and produce the times stored in the Times folder.
- A dummy WebHook that emulates a more complex webhook service. The Dummy WebHook is contained in the `dummy_webhook.py` script and can be launched both for Rasa and Dialogflow specifying the platform as argument. Rasa is default. For example:

```bash
python dummy_webhook.py -p dialogflow
```

- A Dialogflow server placeholder (`dialogflow_local_tester.py`): it receives messages from the user following the Dialogflow API and creates a Dialogflow JSON message that sends to the webhook if needed.

A message follows the path below:

```sequence
User->Dialogflow: msg
Dialogflow->Policy: POST {msg}
Policy->Monitor: WS event
Monitor->Policy: WS oracle
Policy->WebHook: POST {action}
WebHook->Policy: POST {result}
Policy->Monitor: WS event
Monitor->Policy: WS oracle
Policy->Dialogflow: POST {answer}
Dialogflow->User: answer
```

