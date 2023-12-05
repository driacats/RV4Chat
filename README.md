# RV4Chat

## Dialogflow

```bash
python monitorize_dialogflow_agent.py -i input.zip -o output.zip -url https://webhook.address -murl http://monitor.address [-level N]
```
It produces
 - A new zip that makes the given agent monitorizable (it should be uploaded to Dialofgflow);
 - a policy.py script that is launched on the webhook url and allows the monitorization.

Notice that if the start agent had the webhook active for some intent, it is mantained in the policy with a forward.
