	def INTENT_FUNCTION(self):
		available_answers = AVAILABLE_ANSWERS
		message = "{\"fulfillmentMessages\": [{\"text\": [\"" + random.choice(available_answers)+ "\"]}]}"
		oracle_message = {}
		oracle_message["sender"] = "bot"
		oracle_message["receiver"] = "user"
		oracle_message["bot_action"] = "NEXT_ACTION"
		oracle_message = json.dumps(oracle_message)
		if not self.question_oracle(oracle_message):
			return
		self.wfile.write(bytes(message, 'utf8')) 
