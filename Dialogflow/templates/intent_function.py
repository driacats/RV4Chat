	def INTENT_FUNCTION_answer(self):
		available_answers = AVAILABLE_ANSWERS
		message = "{\"fulfillmentMessages\": [{\"text\": [\"" + random.choice(available_answers)+ "\"]}]}"
		oracle_message = {}
		oracle_message["sender"] = "user"
		oracle_message["answer"] = "INTENT_ORACLE"
		oracle_message = json.dumps(oracle_message)
		# oracle_message = "{\"sender\": \"\", \"answer\": \"INTENT_ORACLE\"}"
		oracle = requests.post(self.MONITOR_URL, json=oracle_message)
		if not oracle:
			self.send_error_message()
			return
		self.wfile.write(bytes(message, 'utf8')) 
