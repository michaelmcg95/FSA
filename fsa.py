#! /usr/bin/python3

from collections import defaultdict
from regex import *

class State:
    count = 0
    def __init__(self):
        self.num = State.count
        State.count += 1
        self.terminal = False
        self.transitions = defaultdict(list)

    def make_terminal(self):
        self.terminal = True

    def add_transition(self, char, state):
        self.transitions[char].append(state)

    def __repr__(self):
        s = ""
        for char, states in self.transitions.items():
            if char == "":
                char = "lambda"
            s += f"{char}: {[s.num for s in states]}, "
        return s


class FSA:
    def __init__(self, regex=None, filename=None):
        if regex is not None:
            self.load_from_regex(regex)

        elif filename is not None:
            pass

    def __repr__(self):
        s = ""
        for state in self.states:
            term = ""
            if state.terminal:
                term = "t"
            s += f"{state.num}{term} -- {repr(state)}\n"
        return s
    
    def load_from_regex(self, regex):
        self.states = [State()]
        stack = []
        last_grp_start = self.states[0]
        for tok in tokenize(regex):
            if isinstance(tok, Start_Group):
                stack.append(self.states[-1])
            elif isinstance(tok, End_Group):
                last_grp_start = stack.pop()
            elif isinstance(tok, (Char_Set, Char_Literal)):
                last_grp_start = self.states[-1]
                if hasattr(tok, "char"):
                    tok.char_set = set(tok.char)
                new_state = State()
                for c in tok.char_set:
                    self.states[-1].add_transition(c, new_state)
                self.states.append(new_state)

            else:
                if isinstance(tok, (Zero_Plus, One_Plus)):
                    self.states[-1].add_transition("", last_grp_start)
                if isinstance(tok, (Zero_One, Zero_Plus)):
                    last_grp_start.add_transition("", self.states[-1])

        self.states[-1].make_terminal()

    def test(self, s):
        return True
    
if __name__ == "__main__":
    f = FSA(regex="(1(a(b[cd]*)*8)*)*")
    print(f)