#! /usr/bin/python3

# Michael McGuan
# CS 406 -- Alcon
# Project Milestone 2
# User Interface for FSA simulator
# Due October 10, 2025

from fsa import *
import os
import readline

PROMPT = "> "
ACCEPT_REJECT = {True: "accept", False: "reject"}
HELP_TEXT = '''
This program simulates the operation of finite state automata (FSA).
To get started, try creating a FSA from a file or regular expression (regex).
You can then print its transition graph and test it with strings.

The following commands are available:
help: display information on using the program.
quit: end the program.
load file [filename]: load a FSA from a state transition graph file.
load regex [regex]: load a FSA from a regex expression.
test [options] [string]: check if FSA accepts string. if -b option given
    test using backtracking method
trace: toggle tracing. When activated, display a list of states visited
    when testing strings.
print: print a text description of the FSA's transition graph.
write: save FSA as transition graph file
regex: generate an equivalent regex from FSA.
import [filename]: load FSA from jflap xml file
export: save FSA as jflap xml file
reduce: minimize number of states in a DFA
DFA: convert NFA to DFA
type: check if current automaton is DFA or NFA
label: relabel the states of FSA
'''

def make_fsa(tg):
    """Make a DFA is possible, otherwise make NFA"""
    if tg.is_dfa():
        return DFA(tg=tg)
    return NFA(tg=tg)

def check_overwrite(filename):
    ok_to_write = True
    if os.path.isfile(filename):
        ok_to_write = input("File exists: overwrite? (y/n): ")
        ok_to_write = ok_to_write[0].upper() != 'N'
    return ok_to_write

if __name__ == "__main__":
    print("Welcome to FSA simulator. Type 'help' for instructions.")
    running = True
    trace = False
    my_fsa = None
    while running:
        words = input(PROMPT).lower().split()
        command = words[0]

        # skip empty lines
        if command == "":
            continue
        
        if command in ("exit", "quit", "q"):
            running = False
        elif command == "help":
            print(HELP_TEXT)
        elif command == "trace":
            if trace:
                print("tracing off")
            else:
                print("tracing on")
            trace = not trace
        elif command == "import":
            if len(words) < 2:
                print("Error: no filename given. Usage: 'import <filename>'")
            else:
                filename = words[1]
                if os.path.isfile(filename):
                    try:
                        tg = Transition_Graph(jflap=words[1])
                        my_fsa = make_fsa(tg)
                        print("Imported jflap xml file")
                    except FSA_Error as e:
                        print("Invalid file:", e)
                else:
                    print("Error: cannot open", filename)        
        elif command == "load":
            if len(words) < 2:
                print("Error: Load requires at least 2 arguments")
            filename = None
            if len(words) == 2:
                filename = words[1]
            elif words[1] in ("-f", "file"):
                filename=words[2]
            if filename:
                if os.path.isfile(filename):
                    try:
                        tg = Transition_Graph(filename=filename)
                        my_fsa = make_fsa(tg)
                        print("file loaded")
                    except FSA_Error as e:
                        print("Invalid file:", e)
                else:
                    print("Error: cannot open", filename)
            elif words[1] in ("-r", "regex"):
                my_fsa = NFA(regex=words[2])
                print("regex loaded")           
            else:
                print("Error: unrecognized load option. Use 'file' or 'regex'.")

        elif command == "type":
            if isinstance(my_fsa, DFA):
                print("DFA")
            elif isinstance(my_fsa, NFA):
                print("NFA")
            else:
                print("No automaton loaded")

        # Commands after this point require a FSA to be loaded
        elif my_fsa is None:
            print("Error: no FSA loaded")
        elif command in ("p", "print"):
            print(my_fsa)
        elif command in ("t", "test"):
            if len(words) < 2:
                print("Error: no string given. Usage: 'test <string>'")
            else:
                backtrack = False
                test_string = words[1]
                if len(words) >= 3 and words[1][0] == "-":
                    options = words[1][1:]
                    test_string = words[2]
                    if "b" in options:
                        backtrack = True
                if isinstance(my_fsa, NFA) and backtrack:
                    result = my_fsa.test_backtrack(test_string, trace)
                else:
                    result = my_fsa.test(test_string, trace)
                print(ACCEPT_REJECT[result])
        elif command == "regex":
            print(my_fsa.to_regex())
        elif command == "label":
            my_fsa.label_states()
        elif command == "write":
            if len(words) < 2:
                print("Error: no filename given. Usage: 'write <filename>'")
            elif my_fsa is None:
                print("Error: no FSA loaded")
            else:
                filename = words[1]
                ok_to_write = check_overwrite(filename)
                if ok_to_write:
                    my_fsa.write_file(filename)
                    print("Wrote transition graph to", filename)
                else:
                    print("Write canceled")
        elif command == "reduce":
            if isinstance(my_fsa, DFA):
                num_state_before = len(my_fsa.get_state_list())
                DFA_reduced = my_fsa.reduce()
                num_state_after = len(DFA_reduced.get_state_list())
                reduction = num_state_before - num_state_after
                if reduction == 0:
                    print("DFA is already minimal")
                else:
                    my_fsa = DFA_reduced
                    print(f"Reduced number of states by {reduction}.")
            else:
                print("Error: automaton is not a DFA. Use command <dfa> first.")
        elif command == "dfa":
            if isinstance(my_fsa, DFA):
                print("Automaton is already a DFA")
            else:
                my_fsa = DFA(nfa=my_fsa)
                print("Converted automaton to a DFA")
        elif command == "export":
            if len(words) < 2:
                print("Error: no filename given. Usage: 'export <filename>'")
            else:
                my_fsa.write_jflap(words[1])
                print("Wrote JFLAP xml to", words[1])

        else:
            print(f"Unrecognized command: {command}")