### Factory CAD Example

This chatbot helps a non expert user to place robots inside a factory in order to find the best and safest configuration.
In this example you can find the Dialogflow agent and a dummy monitor that simulates the execution of the CAD virtual system sending right messages back to the chat and taking into account the execution.

The user can perform three actions:
 - add a robot with the global reference frame;
 - add a robot with position related to one of the objects already placed;
 - remove a robot from the factory.

The monitor controls:
 - bot_right: when an object is added with reference to another or removed, the same object must be before inserted on the stage;

In this folder it is provided:
 - The monitor folder;
 - dummy_webhook.py: a dummy factory CAD from cli to emulate the work of a factory CAD. It listens on localhost:8082;
 - the zip of the Diaogflow agent not monitored.

Tests have been done in this way:
 1. Testing the plain Dialogflow agent 
    - upload the AssistantAgent.zip file on Dialogflow;
    - launch ngrok on port 8082
        ```bash
        ngrok http 8082
        ```
    - copy the url provided by ngrok on Dialogflow
    - launch the dummy WebHook server
        ```bash 
        python dummy_webhook.py
        ```
    - add or remove objects!

 2. Testing the instrumented Dialogflow agent
    - Change the fulfillment to "http://localhost:8082" on the agent
    - instrument the Dialogflow agent
        ```bash
        % From the Dialogflow folder
        python3 instrumenter.py -i Examples/Factory/AssistantAgent.zip -o AssistantAgentMonitored.zip -url your_policy_url -murl http://localhost:8081 -level 2
        ```
    - upload the new version of the Dialogflow agent
    - launch the policy
        ```bash
        python output/policy.py
        ```
    - launch the monitor
        ```bash
        Examples/Factory/Monitor/online_monitor.sh Properties/wanted_property.pl 8081
        ```
    - launch the dummy WebHook server
        ```bash 
        python dummy_webhook.py
        ```
    - add or remove objects!
