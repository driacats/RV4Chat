## Rasa

![Rasa Architecture](../.images/RasaArchitecture.png)

To make Rasa monitorable you only have to add the `monitorPolicy` provided in this folder to the policies with the wanted error action.
The `monitorPolicy` should be placed in the `policies` folder that you might need to create.

In your `config.yml` file you should also add:

```yaml
 - name: policies.monitorPolicy.MonitorPolicy
   priority: 6
   error_action: YOUR_ERROR_ACTION
```

Remember to substitute `YOUR_ERROR_ACTION` with an actual error action you defined.