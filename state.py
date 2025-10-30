# Michael McGuan
# CS 406 -- Alcon
# Project Milestone 4
# State class for FSA simulator
# Due October 24, 2025

from collections import defaultdict
# from regex import *

# using dummy class and function defintions for now
class Star_Node:
    pass
class Cat_Node:
    pass
def union_all(nodes):
    pass
def make_node(char):
    pass

class State:
    """This class models a state from a fsa"""
    def __init__(self, label=None):
        self.label = label
        self.outgoing = defaultdict(set)
        self.incoming = defaultdict(set)
        self.GTG_in = set()
        self.GTG_out = set()

    def merge(self, src):
        """merge transitions to/from source into self"""

        def change_outgoing(char, state):
            self.add_transition(char, state)
            state.incoming[char].remove(src)

        def change_incoming(char, state):
            state.add_transition(char, self)
            state.outgoing[char].remove(src)

        src.iterate_over_incoming(change_incoming)
        src.iterate_over_outgoing(change_outgoing)

    def suppress(self):
        """Reroute all possible in/out transition pairs around self.
        Assumes GTG_in and GTF_out sets were already created."""
        loops = []
        non_loops_out = []
        for out_node, dest in self.GTG_out:
            if dest == self:
                loops.append(out_node)
            else:
                non_loops_out.append((out_node, dest))
        non_loops_in = [(in_node, orig) for in_node, orig 
                        in self.GTG_in if orig != self]
        loops_node = Star_Node(union_all(loops))
        for out_node, dest in non_loops_out:
            for in_node, orig, in non_loops_in:
                new_node = Cat_Node(Cat_Node(in_node, loops_node), out_node)
                orig.GTG_out.add((new_node, dest))
                dest.GTG_in.add((new_node, orig))
        for out_node, dest in non_loops_out:
            dest.GTG_in.discard((out_node, self))
        for in_node, orig, in non_loops_in:
            orig.GTG_out.discard((in_node, self))

    def add_transition(self, char, state):
        """Add a transtion from self to state on char"""
        self.outgoing[char].add(state)
        state.incoming[char].add(self)

    def has_outgoing(self):
        return len(self.outgoing) != 0
    
    def has_incoming(self):
        return len(self.incoming) != 0
    
    def iterate_over_outgoing(self, func):
        return State._iterate_over(func, self.outgoing)
    
    def iterate_over_incoming(self, func):
        return State._iterate_over(func, self.incoming)
    
    def make_GTG_sets(self):
        """Make sets of (Regex_Node, state) tuples for this state"""
        self.GTG_in = set()
        self.GTG_out = set()
        for char, state_set in self.outgoing.items():
            for state in state_set:
                self.GTG_out.add((make_node(char), state))
        for char, state_set in self.incoming.items():
            for state in state_set:
                self.GTG_in.add((make_node(char), state))

    @staticmethod
    def _iterate_over(func, state_dict):
        """Apply func to each transition in state_dict"""
        for char, state_set in state_dict.items():
            for state in state_set:
                func(char, state)

    def __str__(self):
        def transitions_to_str(transition_dict):
            s = ""
            for char, states in transition_dict.items():
                s += f"{char}: [{', '.join([s.label for s in states])}], "
            return s[:-2]

        s = f"{transitions_to_str(self.outgoing):25}"
        s += f"{transitions_to_str(self.incoming)}"
        return s
    
    def __repr__(self):
        return "state " + self.label