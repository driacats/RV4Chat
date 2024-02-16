## Caso Utente scrive per primo

```sequence
User->Chat:msg
Chat->Rasa:POST msg
Rasa->Monitor: WS Event
Monitor->Rasa: Oracle
Rasa->Actions: Action
Actions->WebHook: WS request
WebHook->Actions: (Answer, ev)
Actions->Rasa: (Answer, ev)
Rasa->Monitor: WS ev
Monitor->Rasa: Oracle
Rasa->Chat: Answer
```

## Caso Webhook scrive per primo

```sequence
WebHook->Rasa: msg
Rasa->Actions: Action
Actions->Chat: POST msg
Chat->Actions: 200 OK
Actions->Rasa: 200 OK
Rasa->Webhook: 200 OK
```

Quando il timer scatta il webhook manda un messaggio a rasa come se fosse l'utente e questo messaggio triggera un'azione che fa comparire il messaggio su chat.