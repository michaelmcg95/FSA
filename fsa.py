#! /usr/bin/python3

from collections import defaultdict
from regex import *

class State:
    def __init__(self, init=False, final=False, label=None):
        self.label = label
        self.init = init
        self.final = final
        self.transitions = defaultdict(set)
        self.incoming = defaultdict(set)

    # def replace(self, src):
    #     """replace transitions with those of source state"""
    #     self.init = src.init
    #     self.final = src.final
    #     self.transitions = src.transitions
    #     for char, states in src.transitions.items():
    #         for state in states:
    #             state.incoming[char].remove(src)
    #             state.incoming[char].add(self)

    def merge(self, src, overwrite=False):
        """add transitions from source state"""
        if overwrite:
            self.init = src.init
            self.final = src.final
            self.transitions = src.transitions

        for char, states in src.transitions.items():
            if not overwrite:
                combined = self.transitions[char].union(states)
                self.transitions[char] = combined
            for state in states:
                state.incoming[char].remove(src)
                state.incoming[char].add(self)

        for char, states in src.incoming.items():
            combined = self.incoming[char].union(states)
            self.incoming[char] = combined
            for state in states:
                state.transitions[char].remove(src)
                state.transitions[char].add(self)


    def add_transition(self, char, state):
        self.transitions[char].add(state)
        state.incoming[char].add(self)

    def __repr__(self):
        s = ""
        for char, states in self.transitions.items():
            if char == "":
                char = '""'
            s += f"{char}: {[s.label for s in states]}, "
        s += "In: "
        for char, states in self.incoming.items():
                if char == "":
                    char = '""'
                s += f"{char}: {[s.label for s in states]}, "

        return s


class FSA:
    def __init__(self, regex=None, node=None, filename=None):
        if regex is not None:
            self.eval_node(parse(regex))
            self.label_states()
        
        elif node is not None:
            self.eval_node(node)

        elif filename is not None:
            pass

    def __repr__(self):
        s = ""
        for state in self.states:
            init, final = "", ""
            if state.final:
                final = "f"
            if state.init:
                init = "i"
            s += f"{state.label}{init}{final} -- {repr(state)}\n"
        return s
    
    def label_states(self):
        for count, state in enumerate(self.states):
            state.label = count
        
    def eval_node(self, node):
        """Create FSA from a regex parse tree"""
        if isinstance(node, Character_Node):
            init = State(init=True)
            final = State(final=True)
            self.states = [init, final]
            self.init_state = init
            self.final_state = final
            init.add_transition(node.char, final)
        elif isinstance(node, Cat_Node):
            left = FSA(node=node.left)
            right = FSA(node=node.right)
            self.init_state = left.init_state
            left.final_state.merge(right.init_state, overwrite=True)
            left.final_state.init = False
            self.final_state = right.final_state
            self.states = left.states + right.states[1:]
        if isinstance(node, Union_Node):
            left = FSA(node=node.left)
            right = FSA(node=node.right)
            left.init_state.merge(right.init_state)
            right.final_state.merge(left.final_state)
            self.states = left.states[:-1] + right.states[1:]
            
    def test(self, s):
        return True
    
if __name__ == "__main__":
    print(FSA(regex="ab+cd"))
