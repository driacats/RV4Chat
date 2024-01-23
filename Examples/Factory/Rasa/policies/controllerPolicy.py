from typing import List, Dict, Text, Any
from rasa.core.policies.policy import Policy, PolicyPrediction
from rasa.shared.core.trackers import DialogueStateTracker
from rasa.shared.core.generator import TrackerWithCachedStates
from rasa.shared.core.domain import Domain
from rasa.shared.core.constants import ACTION_LISTEN_NAME
from rasa.engine.recipes.default_recipe import DefaultV1Recipe
from rasa.engine.training.fingerprinting import Fingerprintable
from rasa.engine.storage.storage import ModelStorage
from rasa.engine.storage.resource import Resource
from rasa.engine.graph import ExecutionContext
import json
from websocket import create_connection

@DefaultV1Recipe.register([DefaultV1Recipe.ComponentType.POLICY_WITHOUT_END_TO_END_SUPPORT], is_trainable=False)
class ControllerPolicy(Policy):

	# The function __init__ initializes the class.
	# With respect to the super class it is initialized the socket client that will connect to the monitor.
	def __init__(self, cls, model_storage, resource, execution_context, error_action="utter_error_message"):
		# We call the super function
		super().__init__(cls, model_storage, resource, execution_context)
		# Set the error_action
		self.error_action = error_action

	# The function train is called during the training phase of rasa.
	# In our case the monitor is deterministic, there is no training phase, so we can simply pass it.
	def train(self, training_trackers:List[TrackerWithCachedStates], domain:Domain, **kwargs:Any) -> Fingerprintable:
		pass

	# The function build_user_message builds the message for the monitor for user inputs
	def build_user_message(self, tracker, domain):
		
		msg_obj = {}
		msg_obj["sender"] = "user"
		msg_obj["receiver"] = "bot"
		
		intent = {}
		intent["name"] = tracker.latest_message.intent["name"]
		intent["confidence"] = tracker.latest_message.intent["confidence"]
		msg_obj["intent"] = intent
		
		entities = {}
		for entity in tracker.latest_message.entities:
			entities[entity["entity"]] = entity["value"]
		msg_obj["entities"] = entities
		
		return json.dumps(msg_obj)

	# The function build_user_message builds the message for the monitor for bot actions
	def build_bot_message(self, tracker, domain):
		
		msg_obj = {}
		msg_obj["sender"] = "bot"
		msg_obj["receiver"] = "user"
		
		msg_obj["bot_action"] = str(tracker.latest_action_name)
		
		return json.dumps(msg_obj)

	# The function predict_action_probabilities is called when a message arrives to rasa and returns a prediction.
	def predict_action_probabilities(self, tracker:DialogueStateTracker, domain:Domain, **kwargs:Any) -> PolicyPrediction:

		# We start with the default predictions (all zeros)
		prediction = self._default_predictions(domain)
		# If the latest action executed was the error one, we have to stop and wait for a user input
		if tracker.latest_action_name == self.error_action:
			prediction[domain.index_for_action(ACTION_LISTEN_NAME)] = 1.0
			return self._prediction(prediction)
		# If the latest action was listen we are on the "Intent" step of the story,
		# else we are on the actions
		if not tracker.latest_action_name == ACTION_LISTEN_NAME:
			ws = create_connection("ws://localhost:5052")
			# We send it to the monitor and wait for the answer.
			ws.send(self.build_bot_message(tracker, domain))
			oracle = ws.recv()
			ws.close()
		else:
			# Create a connection to the monitor
			ws = create_connection("ws://localhost:5052")
			# We send it to the monitor and wait for the answer.
			ws.send(self.build_user_message(tracker, domain))
			oracle = ws.recv()
			ws.close()
		# If the monitor returns False then the message is not accepted and the action used is the error one.
		# Instead we do nothing, leaving the bot follow its routine.
		oracle = json.loads(oracle)
		if oracle["verdict"] == False:
			prediction[domain.index_for_action(self.error_action)] = 1.0
			return self._prediction(prediction)

	@classmethod
	def load(cls, config: Dict[Text, Any], model_storage: ModelStorage, resource: Resource, execution_context: ExecutionContext, **kwargs: Any):
		return cls(config, model_storage, resource, execution_context)

	def get_default_config() -> Dict[Text, Any]:
		return {"priority": 2}

	@classmethod
	def _metadata_filename(cls):
		return "controller_policy.json"

	def _metadata(self):
		return{
			"priority": self.priority
		}


class ControllerFingerprintable(Fingerprintable):
	def fingerprint(self) -> Text:
		# Implement the fingerprint method as needed
		# This method should return a string that uniquely identifies the state of the object
		return "ControllerPolicy"
