#! /usr/bin/python3

# Michael McGuan
# CS 406 -- Alcon
# Project Milestone 2
# User Interface for FSA simulator
# Due October 10, 2025

# from fsa import FSA
# using dummy FSA for now

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

class FSA:
    """Stub FSA that accepts all strings"""
    def __init__(self, *args, **kwargs):
        pass
    def test(self, *args, **kwargs):
        return True
    def __str__(self):
        return "Stub FSA for UI prototype"
    def to_regex(self):
        return "Coming soon."
    
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
        elif command == "print":
            print(my_fsa)
        elif command == "test":
            if len(words) < 2:
                print("Error: no string given. Usage: 'test <string>'")
            elif my_fsa is None:
                print("Error: no FSA loaded")
            else:
                result = my_fsa.test(words[1], trace)
                print(ACCEPT_REJECT[result])
        elif command == "load":
            try:
                if len(words) < 3:
                    print("Error: missing argument. Load requires 2 arguments")
                elif words[1] == "file":
                    my_fsa = FSA(filename=words[2])
                    print("file loaded")
                elif words[1] == "regex":
                    my_fsa = FSA(regex=words[2])
                    print("regex loaded")           
                else:
                    print("Error: unrecognized option. Use 'file' or 'regex'.")
            except SyntaxError as e:
                print(f"Error: {e}")
        elif command == "regex":
            if my_fsa is None:
                print("Error: no FSA loaded")
            else:
                print(my_fsa.to_regex())
        else:
            print(f"Unrecognized command: {command}")