#! /usr/bin/python3

from collections import defaultdict
from regex import *

class State:
    count = 0

    @classmethod
    def reset_count(cls):
        cls.count = 0

    def __init__(self, init=False, label=None):
        if label is None:
            self.label = State.count
            State.count += 1
        self.init = init
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
                char = "\"\""
            s += f"{char}: {[s.label for s in states]}, "
        return s


class FSA:
    def __init__(self, regex=None, filename=None):
        if regex is not None:
            State.reset_count()
            self.load_from_regex(regex)

        elif filename is not None:
            pass

    def __repr__(self):
        s = ""
        for state in self.states:
            init, term = "", ""
            if state.terminal:
                term = "t"
            if state.init:
                init = "i"
            s += f"{state.label}{term}{init} -- {repr(state)}\n"
        return s
    
    def load_from_regex(self, regex):
        """Create FSA from a regex"""
        self.start_state = State(init=True)
        self.states = [self.start_state]
        stack = []
        last_grp_start = self.start_state
        for tok in tokenize(regex):
            if isinstance(tok, Start_Group):
                stack.append(self.states[-1])
            elif isinstance(tok, End_Group):
                if stack == []:
                    raise SyntaxError
                last_grp_start = stack.pop()
            elif isinstance(tok, (Char_Set, Char_Literal)):
                last_grp_start = self.states[-1]
                new_state = State()
                if isinstance(tok, Char_Literal):
                    self.states[-1].add_transition(tok.char, new_state)
                else:
                    for c in tok.char_set:
                        self.states[-1].add_transition(c, new_state)
                self.states.append(new_state)

            else:
                if isinstance(tok, (Zero_Plus, One_Plus)):
                    self.states[-1].add_transition("", last_grp_start)
                if isinstance(tok, (Zero_One, Zero_Plus)):
                    last_grp_start.add_transition("", self.states[-1])

        if stack != []:
            raise SyntaxError
        self.states[-1].make_terminal()

    def test(self, s):
        return True
    
if __name__ == "__main__":
    print(FSA(regex="(1(a(b[cd]*)*8)*)*"))
    print(FSA(regex="[abc]12"))
