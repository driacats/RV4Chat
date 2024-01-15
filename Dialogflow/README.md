## RV4Dialogflow

Dialogflow answers can be of two types:
    1. Plain answers;
    1. Webhook answers.

The first ones are managed internally simply picking up randomly from the answer set provided, the second ones are asked to an external service and once received are only forwarded to che chat.

To build a Runtime Verification system for Dialogflow it is needed an additional level, that we will call **Policy** that will manage the flow of the chat, receiving the user inputs and the answers before they are sent on the chat, both the plain and the webhook ones.

If for example the user writes "Hello" on the chat the flow should follow this sequence:

```sequence
User->Dialogflow: "Hello!"
Dialogflow->Policy: "{user: "Hello!"}"
Policy->Monitor: "{user: utter_hello}"
Monitor->Policy: Ok
Policy->Policy: answer_choice()
Policy->Monitor: "{bot: utter_how_are_you}"
Monitor->Policy: Ok
Policy->Dialogflow: "{bot:"Hello, how are you?"}"
Dialogflow->User: "Hello, how are you?"
```





```sequence
User->Dialogflow: "What's the weather?"
Dialogflow->Policy: "{user: "What's the weather?"}"
Policy->Monitor: "{user: ask_weather}"
Monitor->Policy: Ok
Policy->WebHook: "{user: weather, position: XYZ, time: 00:00}"
WebHook->Policy: "{weather: sunny, event: sun_answer, text"Today is sunny!"}"
Policy->Monitor: "{bot: sun_answer}"
Monitor->Policy: Ok
Policy->Dialogflow: "{bot:"Today is sunny!"}"
Dialogflow->User: "Today is sunny!"
```

