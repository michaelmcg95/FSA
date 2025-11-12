#! /usr/bin/python3

# Michael McGuan
# CS 406 -- Alcon
# Project Milestone 2
# User Interface for FSA simulator
# Due October 10, 2025

from fsa import *
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
load file [filename]: load a FSA from a state transition file.
load regex [regex]: load a FSA from a regex expression.
test [string]: check if FSA accepts string.
trace: toggle tracing. When activated, display a list of states visited
    when testing strings.
print: print a text description of the FSA's transition graph.
regex: generate an equivalent regex from FSA.
'''
    
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
        
        if command in ("exit", "quit"):
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
                try:
                    my_fsa = NFA(jflap=words[1])
                    print("Imported jflap xml file")
                except Exception as e:
                    print(e)
        elif command == "load":
            if len(words) < 3:
                print("Error: missing argument. Load requires 2 arguments")
            try:
                if words[1] == "file":
                    my_fsa = NFA(filename=words[2])
                    print("file loaded")
                elif words[1] == "regex":
                    my_fsa = NFA(regex=words[2])
                    print("regex loaded")           
                else:
                    print("Error: unrecognized option. Use 'file' or 'regex'.")
            except (FSA_Error, SyntaxError) as e:
                print("Error in FSA file:", e)
            except Exception as e:
                print(e)

        # Commands after this point require a FSA to be loaded
        elif my_fsa is None:
            print("Error: no FSA loaded")
        elif command == "print":
            print(my_fsa)
        elif command == "test":
            if len(words) < 2:
                print("Error: no string given. Usage: 'test <string>'")
            else:
                result = my_fsa.test(words[1], trace)
                print(ACCEPT_REJECT[result])
        elif command == "regex":
            print(my_fsa.to_regex())
        elif command == "write":
            if len(words) < 2:
                print("Error: no filename given. Usage: 'write <filename>'")
            elif my_fsa is None:
                print("Error: no FSA loaded")
            else:
                my_fsa.write_file(words[1])
                print("Wrote transition graph to", words[1])
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
                print("Your automaton is already a DFA")
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