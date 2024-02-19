:- module('spec', [trace_expression/2, match/2]).
:- use_module(monitor('deep_subdict')).
match(_event, help_word) :- deep_subdict(_{'intent':_{'confidence':_,'name':"help_word"},'receiver':"bot",'sender':"user"}, _event).
match(_event, help_word(T)) :- deep_subdict(_{'timestamp':T,'entities':_,'intent':_{'confidence':_,'name':"help_word"},'receiver':"bot",'sender':"user"}, _event).
match(_event, undo_word) :- deep_subdict(_{'timestamp':_,'entities':_,'intent':_{'confidence':_,'name':"undo_word"},'receiver':"bot",'sender':"user"}, _event).
match(_event, help_called_on_time(Helpt)) :- deep_subdict(_{'timestamp':T,'bot_action':"help_called",'receiver':"user",'sender':"bot"}, _event), >((T-Helpt), 4).
match(_event, help_called) :- deep_subdict(_{'bot_action':"help_called",'receiver':"user",'sender':"bot"}, _event).
match(_event, utter_stop_help) :- deep_subdict(_{'bot_action':"utter_stop_help",'receiver':"user",'sender':"bot"}, _event).
match(_event, utter_help) :- deep_subdict(_{'timestamp':_,'bot_action':"utter_help",'receiver':"user",'sender':"bot"}, _event).
match(_event, relevant) :- match(_event, help_word).
match(_event, relevant) :- match(_event, utter_help).
match(_event, relevant) :- match(_event, undo_word).
match(_event, relevant) :- match(_event, help_called).
match(_event, relevant) :- match(_event, utter_stop_help).
match(_, any).
trace_expression('Main', Main) :- Main=((relevant>>star(Contact));1), Contact=var(time, ((help_word(var(time)):eps)*((utter_help:eps)*(Undo\/Help)))), Undo=((undo_word:eps)*(utter_stop_help:eps)), Help=(help_called_on_time(var(time)):eps).
