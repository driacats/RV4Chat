def INTENT_FUNCTION():
	available_answers = AVAILABLE_ANSWERS
	msg = {}
	msg['fulfillmentMessages'] = [{'text': {'text': [random.choice(available_answers)]}}]
	return msg
