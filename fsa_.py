#! /usr/bin/python3

# Michael McGuan
# CS 406 -- Alcon
# Project Milestone 5
# FSA class for FSA simulator
# Due October 31, 2025

from collections import defaultdict
import xml.etree.ElementTree as ET

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

NULL_CHAR = "~"
LAMBDA_CHAR = "^"
LABEL_CHAR = "@"
COMMENT_CHAR = "#"
START_CHAR = "!"
FINAL_CHAR = "*"

class State:
    def __init__(self, label=None):
        self.label = label
        self.outgoing = defaultdict(set)
        self.incoming = defaultdict(set)
        self.GTG_in = set()
        self.GTG_out = set()

    def merge(self, src):
        """take all transitions to/from source"""

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

class FSA:
    def __init__(self, filename=None, jflap=None):
        self.init_state = None
        self.final_states = set()

        if filename is not None:
            self.load_file(filename)

        elif jflap is not None:
            self.load_jflap(jflap)
    
    def load_jflap(self, filename):
        """Load from jflap xml file"""
        tree = ET.parse(filename)
        automaton = tree.find("automaton")
        states = {}
        for elem in automaton:
            if elem.tag == "state":
                label = elem.attrib["name"]
                new_state = State(label)
                states[elem.attrib["id"]]= new_state
                if elem.find("initial") is not None:
                    self.init_state = new_state
                if elem.find("final") is not None:
                    self.final_states.add(new_state)
            elif elem.tag == "transition":
                from_state = states[elem.find("from").text]
                to_state = states[elem.find("to").text]
                char = elem.find("read").text
                if char is None:
                    char = LAMBDA_CHAR
                from_state.add_transition(char, to_state)
                
    def load_file(self, filename):
        "Load from text file"
        with open(filename, "r") as file:
            lines = file.readlines()

        lines_words = [l.split() for l in lines if l[0] != COMMENT_CHAR]
        lines_words = [words for words in lines_words if len(words) > 0]

        state_label_dict = {}
        transitions = defaultdict(list)

        current_state = None
        for words in lines_words:
            first_char = words[0][0]
            if first_char == LABEL_CHAR:
                if len(words[0]) < 2:
                    raise SyntaxError("Missing state label")
                label = words[0][1:]
                current_state = State(label=label)
                state_label_dict[label] = current_state
            elif first_char == START_CHAR:
                if self.init_state is not None:
                    raise SyntaxError("Multiple initial states")
                self.init_state = current_state
            elif first_char == FINAL_CHAR:
                self.final_states.add(current_state)
            else:
                for word in words[1:]:
                    transitions[current_state.label].append((first_char, word))
        if self.init_state is None:
            raise SyntaxError("No initial state")
        if len(self.final_states) == 0:
            raise SyntaxError("No final state")
        
        for src_label, trans in transitions.items():
            for c, dest_label in trans:
                state = state_label_dict[src_label]
                dest_state = state_label_dict[dest_label]
                state.add_transition(c, dest_state)

    def label_states(self):
        """Assign numeric labels to states"""
        for count, state in enumerate(self.get_state_list()):
            state.label = str(count)

    def __repr__(self):
        s = f"if {'Label':11}{'Outgoing Transitions':25}Incoming Transitions\n"
        s += ("-"*70 + "\n")
        for state in self.get_state_list():
            state_type = START_CHAR if state == self.init_state else "-"
            state_type += FINAL_CHAR if state in self.final_states else "-"
            s += f"{state_type} {state.label:10} {str(state)}\n"
        
        return s 
    
    def write_file(self, filename="tg"):
        """Write transition graph to file"""
        states = self.get_state_list()
        with open(filename, "w") as file:
            for state in states:
                file.write(LABEL_CHAR + state.label + "\n")
                if state == self.init_state:
                    file.write(START_CHAR + "\n")
                if state in self.final_states:
                    file.write(FINAL_CHAR + "\n")
                for char, state_list in state.outgoing.items():
                    dest_states = " ".join([s.label for s in state_list])
                    file.write(f"{char}: {dest_states}\n")
                file.write("\n");

    def get_state_list(self):
        """Get list of reachable states in DFS traversal order."""
        state_list = []
        to_visit = [self.init_state]
        visited = set()

        while len(to_visit) > 0:
            state = to_visit.pop()
            if state not in visited:
                visited.add(state)
                for state_set in state.outgoing.values():
                    for st in state_set:
                        to_visit.append(st)
                state_list.append(state)
        return state_list

    def test(self, s, trace=False):
        """Test if the automaton accepts a string"""
        def print_trace(trans, label, str):
            print(f"{label:<13}{trans:15}{str}")

        def try_all_transitions(state, i, try_lambda=False):            
            if try_lambda:
                char = LAMBDA_CHAR
                next_ind = i
            else:
                char = s[i]
                next_ind = i + 1
            print_char = LAMBDA_CHAR if try_lambda else char
            for next_state in state.outgoing.get(char, ()):
                if trace:
                    print_trace(print_char, next_state.label, s[next_ind:])
                if _test(s, next_ind, next_state):
                    return True
            return False

        if trace:
            print("State         In Transition  Remaining String")
            print("-" * 50)
            print_trace("(start)", self.init_state.label, s)

        visit_ind = defaultdict(set)

        def _test(s, index, state):
            # check if state visited at same index to avoid infinite recursion
            if index in visit_ind[state]:
                if trace:
                    print(f"{state.label}: backtracking to avoid infinite loop.")
                return False
            visit_ind[state].add(index)

            # Success: reached end of string in final state
            if index == len(s) and state in self.final_states:
                return True
            
            # Try all lambda transitions
            if try_all_transitions(state, index, try_lambda=True):
                return True
                     
            # At end of string but not in final state
            if index == len(s):
                if trace:
                    print(state.label, end="")
                    print(": At end of string but not in final state.")
                return False
            
            # Try non-lambda transitions
            if try_all_transitions(state, index):
                return True

            # No viable transitions found
            if trace:
                msg = f"No path from {state.label} with {s[index:]}"
                print(msg)
            return False

        if s == LAMBDA_CHAR:
            s = ""
        accepted = _test(s, 0, self.init_state)
        if trace:
            if accepted:
                print(f"{s} accepted")
            else:
                print(f"{s} rejected")
        return accepted
