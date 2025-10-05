#! /usr/bin/python3
# User Interface for FSA simulator

from fsa import FSA

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
            else:
                result = my_fsa.test(words[1], trace)
                print(ACCEPT_REJECT[result])
        elif command == "load":
            if len(words) < 3:
                print("Error: missing argument. Load requires 2 arguments")
            elif words[1] == "file":
                my_fsa = FSA(filename=words[2])
            elif words[1] == "regex":
                my_fsa = FSA(regex=words[2])
            else:
                print("Error: unrecognized option. Use 'file' or 'regex'.")
        elif command == "regex":
            print(my_fsa.to_regex())
        else:
            print(f"Unrecognized command: {command}")