:- module('spec', [trace_expression/2, match/2]).
:- use_module(monitor('deep_subdict')).
match(_event, commit_suicide) :- deep_subdict(_{'entities':_,'intent':_{'confidence':_,'name':"commit_suicide"},'receiver':"bot",'sender':"user"}, _event).
match(_event, utter_against_suicide) :- deep_subdict(_{'bot_action':"utter_against_suicide",'receiver':"user",'sender':"bot"}, _event).
match(_event, help_word) :- deep_subdict(_{'entities':_,'intent':_{'confidence':_,'name':"help_word"},'receiver':"bot",'sender':"user"}, _event).
match(_event, undo_word) :- deep_subdict(_{'entities':_,'intent':_{'confidence':_,'name':"undo_word"},'receiver':"bot",'sender':"user"}, _event).
match(_event, utter_help) :- deep_subdict(_{'bot_action':"utter_help",'receiver':"user",'sender':"bot"}, _event).
match(_event, relevant) :- match(_event, commit_suicide).
match(_event, relevant) :- match(_event, utter_against_suicide).
match(_event, relevant) :- match(_event, help_word).
match(_event, relevant) :- match(_event, utter_help).
match(_event, relevant) :- match(_event, undo_word).
match(_, any).
trace_expression('Main', Main) :- Main=((relevant>>star(app(HelpAgainstSuicide, [3])));1), HelpAgainstSuicide=gen(['n'], guarded((var('n')>0), (star((Help\/Undo))*((commit_suicide:eps)*((utter_against_suicide:eps)*app(HelpAgainstSuicide, [(var('n')-1)])))), Help)), Help=((help_word:eps)*(utter_help:eps)), Undo=((undo_word:eps)*(utter_help:eps)).
