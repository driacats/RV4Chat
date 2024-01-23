:- module(spec, [(trace_expression/2), (match/2)]).
:- use_module(monitor(deep_subdict)).
:- use_module(library(clpr)).
match(_event, msg_user_to_bot_et) :- deep_subdict(_event, _{sender:"user", receiver:"bot"}).
match(_event, msg_bot_to_user_et) :- deep_subdict(_event, _{sender:"bot", receiver:"user"}).
match(_event, add_object_et) :- deep_subdict(_event, _{intent:_{name:"add_object", confidence:_}, entities:_{object:_, posX:_, posY:_}}).
match(_event, add_object_rel_et(Obj)) :- deep_subdict(_event, _{intent:_{name:"add_relative_object", confidence:_}, entities:_{object:_, relPos:_, relName:Obj}}).
match(_event, remove_object_et(Obj)) :- deep_subdict(_event, _{intent:_{name:"remove_object", confidence:_}, entities:_{relName:Obj}}).
match(_event, object_added_et(Obj)) :- deep_subdict(_event, _{bot_action:"utter_add_object", aux:_{name:Obj}}).
match(_event, object_added_rel_et(Obj)) :- deep_subdict(_event, _{bot_action:"utter_add_relative_object", aux:_{name:Obj}}).
match(_event, object_removed_et) :- deep_subdict(_event, _{bot_action:"utter_remove_object"}).
match(_event, irrelevant_et) :- deep_subdict(_event, _{bot_action:"send_info"}).
match(_event, irrelevant_et) :- deep_subdict(_event, _{bot_action:"action_reset_all_slots"}).
match(_event, irrelevant_et) :- deep_subdict(_event, _{bot_action:"send_relative_info"}).
match(_event, irrelevant_et) :- deep_subdict(_event, _{bot_action:"send_remove_info"}).
match(_event, relevant_et) :- not(match(_event, irrelevant_et)).
match(_event, any_et) :- deep_subdict(_event, _{}).
match(_event, none_et) :- not(match(_event, any_et)).
trace_expression('Main', Main) :- (Main=((relevant_et>>AddObject);1)),
	(AddObject=var(obj, ((msg_user_to_bot_et/\add_object_et)*((msg_bot_to_user_et/\object_added_et(var(obj)))*(app(AddObjectRel, [var(obj)])|optional(AddObject)))))),
	(AddObjectRel=gen([obj], (((msg_user_to_bot_et/\remove_object_et(var(obj)))*(msg_bot_to_user_et/\object_removed_et))\/var(obj1, ((msg_user_to_bot_et/\add_object_rel_et(var(obj)))*((msg_bot_to_user_et/\object_added_rel_et(var(obj1)))*(optional(app(AddObjectRel, [var(obj1)]))|optional(app(AddObjectRel, [var(obj)]))))))))).
