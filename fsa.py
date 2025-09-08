#! /usr/bin/python3

from collections import defaultdict
from regex import *

LABEL_CHAR = "@"
COMMENT_CHAR = "#"
START_CHAR = "!"
FINAL_CHAR = "*"

class State:
    def __init__(self, label=None):
        self.label = label
        self.transitions = defaultdict(set)
        self.incoming = defaultdict(set)

    def merge(self, src):
        """take all transitions to/from source"""

        def change_outgoing(char, state):
            self.add_transition(char, state)
            state.incoming[char].remove(src)

        def change_incoming(char, state):
            state.transitions[char].remove(src)
            state.add_transition(char, self)

        src.iterate_over_incoming(change_incoming)
        src.iterate_over_transitions(change_outgoing)

    def add_transition(self, char, state):
        self.transitions[char].add(state)
        state.incoming[char].add(self)

    def has_outgoing(self):
        return len(self.transitions) != 0
    
    def has_incoming(self):
        return len(self.incoming) != 0
    
    def iterate_over_transitions(self, func):
        return State._iterate_over(func, self.transitions)
    
    def iterate_over_incoming(self, func):
        return State._iterate_over(func, self.incoming)

    @staticmethod
    def _iterate_over(func, state_dict):
        """Apply func to each transition in state_dict"""
        for char, state_set in state_dict.items():
            for state in state_set:
                func(char, state)

    def __repr__(self):
        def transitions_to_str(transition_dict):
            s = ""
            for char, states in transition_dict.items():
                if char == "":
                    char = '""'
                s += f"{char}: [{', '.join([s.label for s in states])}], "
            return s[:-2]

        s = f"Out -> {transitions_to_str(self.transitions):25}"
        s += f"In <- {transitions_to_str(self.incoming)}"
        return s

class FSA:
    def __init__(self, regex=None, node=None, filename=None):
        if regex is not None:
            self.eval_node(parse(regex))
            self.label_states()
        
        elif node is not None:
            self.eval_node(node)
            self.label_states()

        elif filename is not None:
            self.load_file(filename)
    
    def load_file(self, filename):
        with open(filename, "r") as file:
            lines = file.readlines()

        lines_words = [l.split() for l in lines if l[0] != COMMENT_CHAR]
        lines_words = [words for words in lines_words if len(words) > 0]

        state_label_dict = {}
        self.final_states = set()
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
                self.init_state = current_state
            elif first_char == FINAL_CHAR:
                self.final_states.add(current_state)
            else:
                if first_char == LAMBDA_CHAR:
                    first_char = ""
                for word in words[1:]:
                    transitions[current_state.label].append((first_char, word))
        
        for src_label, trans in transitions.items():
            for c, dest_label in trans:
                state = state_label_dict[src_label]
                dest_state = state_label_dict[dest_label]
                state.add_transition(c, dest_state)

    def label_states(self):
        for count, state in enumerate(self.get_state_list()):
            state.label = str(count)

    def __repr__(self):
        s = ""
        for state in self.get_state_list():
            state_type = START_CHAR if state == self.init_state else "-"
            state_type += FINAL_CHAR if state in self.final_states else "-"
            s += f"{state_type} {state.label:10} {repr(state)}\n"
        
        return s 

    def get_state_list(self):
        """Get list of reachable states in DFS traversal order."""
        state_list = []
        to_visit = [self.init_state]
        visited = set()

        while len(to_visit) > 0:
            state = to_visit.pop()
            if state not in visited:
                visited.add(state)
                for state_set in state.transitions.values():
                    for st in state_set:
                        to_visit.append(st)
                state_list.append(state)
        return state_list
        
    def eval_union_node(self, node):
        """Create FSA from regex union node"""
        left = FSA(node=node.left)
        right = FSA(node=node.right)
        for childFSA in left, right:
            if childFSA.init_state.has_incoming():
                new_init = State()
                new_init.add_transition("", childFSA.init_state)
                childFSA.init_state = new_init
        left.init_state.merge(right.init_state)
        self.init_state = left.init_state
        self.final_states = set.union(left.final_states, right.final_states)
        if right.init_state in self.final_states:
            self.final_states.remove(right.init_state)
            self.final_states.add(left.init_state)

    def eval_cat_node(self, node):
        """Create FSA from regex cat node"""
        left = FSA(node=node.left)
        right = FSA(node=node.right)
        to_merge = []
        for state in left.final_states:
            if state.has_outgoing():
                new_state = State()
                state.add_transition("", new_state)
                to_merge.append(new_state)
            else:
                to_merge.append(state)
        for state in to_merge:
            right.init_state.merge(state)
        self.init_state = left.init_state
        self.final_states = right.final_states


    def eval_star_node(self, node):
        """Create FSA from regex star node"""
        child = FSA(node=node.child)
        self.init_state = child.init_state
        to_merge = []
        for state in child.final_states:
            if state != child.init_state:
                if state.has_outgoing():
                    new_state = State()
                    state.add_transition("", new_state)
                    to_merge.append(new_state)
                else:
                    to_merge.append(state)
        for state in to_merge:
            child.init_state.merge(state)
        self.init_state = child.init_state
        self.final_states = set([child.init_state])

    def eval_leaf_node(self, char=None):
        """Create FSA from character, lambda, or null node"""
        init = State()
        self.init_state = init
        self.final_states = set()
        if char is not None:
            if char == "":
                final = init
            else:
                final = State()
                init.add_transition(char, final)
            self.final_states.add(final)

    def eval_node(self, node):
        """Create FSA from a regex parse tree"""
        if isinstance(node, Character_Node):
            self.eval_leaf_node(node.char)

        elif isinstance(node, Null_Node):
            self.eval_leaf_node()
        
        elif isinstance(node, Lambda_Node):
            self.eval_leaf_node("")

        elif isinstance(node, Cat_Node):
            self.eval_cat_node(node)

        elif isinstance(node, Union_Node):
            self.eval_union_node(node)

        elif isinstance(node, Star_Node):
            self.eval_star_node(node)
          
    def test(self, s, trace=False):
        def print_trace(trans, label, str):
            print(f"{trans:15}{label:<13} {str}")

        if trace:
            print("Transition     State         Remaining String")
            print("-" * 50)
            print_trace("(none)", self.init_state.label, s)
        visit_ind = {}

        def _test(s, index, state):
            # check if state visited at same index to avoid infinite recursion
            if visit_ind.get(state, -1) == index:
                if trace:
                    print("Backtracking to avoid infinite loop.")
                return False
            visit_ind[state] = index

            # Success: reached end of string in final state
            if index == len(s) and state.final:
                return True
            
            # Try all lambda transitions
            if "" in state.transitions:
                for next_state in state.transitions[""]:
                    if trace:
                        print_trace('""', next_state.label, s[index:])
                    if _test(s, index, next_state):
                        return True 
                     
            # Failed: At end of string but not in final state
            if index == len(s):
                return False
                
            c = s[index]
            # Try all transitions from current character
            if c in state.transitions:
                for next_state in state.transitions[c]:
                    if trace:
                        print_trace(c, next_state.label, s[index + 1:])
                    if _test(s, index + 1, next_state):
                        return True
            if trace:
                print("No path from this state. Backtracking to previous.")
            return False

        accepted = _test(s, 0, self.init_state)
        if trace:
            if accepted:
                print(f"{s} accepted")
            else:
                print(f"{s} rejected")
        return accepted

if __name__ == "__main__":
    # a = FSA(regex="~*")
    # print(a)
    # a = FSA(regex="cd*")
    # print(a)
    # print(a.test("abc"))

    a = FSA(filename="a")
    print(a)

