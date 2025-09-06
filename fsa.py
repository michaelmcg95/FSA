#! /usr/bin/python3

from collections import defaultdict
from regex import *

class State:
    def __init__(self, final=False, label=None):
        self.label = label
        self.final = final
        self.transitions = defaultdict(set)
        self.incoming = defaultdict(set)

    def merge(self, src):
        """add transitions to/from source state into self"""
        self.final = src.final
        for char, states in src.transitions.items():
            for state in states:
                self.transitions[char].add(state)
                state.incoming[char].remove(src)
                state.incoming[char].add(self)

        for char, states in src.incoming.items():
            for state in states:
                self.incoming[char].add(state)
                state.transitions[char].remove(src)
                state.transitions[char].add(self)

    def has_outgoing(self):
        return len(self.transitions) != 0
    
    def has_incoming(self):
        return len(self.incoming) != 0

    def redir_trans(self, char, old_state, new_state):
        self.transitions[char].remove(old_state)
        self.add_transition(char, new_state)

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
            tree = parse(regex)
            self.eval_node(parse(regex))
            self.label_states()
        
        elif node is not None:
            self.eval_node(node)

        elif filename is not None:
            self.load_file(filename)
    
    def load_file(self, filename):
        with open(filename, "r") as file:
            lines = file.readlines()
        lines = [l for l in lines if l[0] not in ('#', '\n')]
        states = {}
        transitions = defaultdict(list)
        label = None
        current_state = None
        for line in lines:
            c = line[0]
            words = line.split()
            if c == '@':
                label = words[0][1:]
                current_state = State(label=label)
                states[label] = current_state
            elif c == '!':
                self.init_state = current_state
            elif c == '$':
                current_state.final = True
            else:
                if c == "^":
                    c = ""
                for word in words[1:]:
                    transitions[current_state.label].append((c, word))
        
        for src_label, trans in transitions.items():
            for c, dest_label in trans:
                state = states[src_label]
                dest_state = states[dest_label]
                state.add_transition(c, dest_state)

    def label_states(self):
        def enum_label(states):
            for count, state in enumerate(states):
                state.label = count
        self.traverse_states(aggregator=enum_label)

    def __repr__(self):
        def make_repr(state):
            final = "*" if state.final else ""
            return f"{state.label}{final} -- {repr(state)}"
        
        s = f"Start: {self.init_state.label}\n"
        return s + self.traverse_states(func=make_repr, aggregator="\n".join)

    def traverse_states(self, func=lambda x: x, aggregator=lambda x: x ):
        """DFS traversal of states. Make list of values by applying func to 
        each state. Return result of applying aggregator to this list."""
        result = []
        to_visit = [self.init_state]
        visited = set()

        while len(to_visit) > 0:
            state = to_visit.pop()
            if state not in visited:
                visited.add(state)
                for state_set in state.transitions.values():
                    for st in state_set:
                        to_visit.append(st)
                result.append(func(state))
        return aggregator(result)
        
    def eval_union_node(self, node):
        """Create FSA from regex union node"""
        left = FSA(node=node.left)
        right = FSA(node=node.right)
        for childFSA in left, right:
            # add new initial state if child's init has incoming transition
            if childFSA.init_state.has_incoming():
                new_init = State()
                new_init.add_transition("", childFSA.init_state)
                childFSA.init_state = new_init
            # add new final state if child's final has outgoing transition
            if childFSA.final_state.has_outgoing():
                new_final = State(final=True)
                childFSA.final_state.add_transition("", new_final)
                childFSA.final_state.final = False
                childFSA.final_state = new_final
        left.init_state.merge(right.init_state)
        left.final_state.merge(right.final_state)
        self.init_state = left.init_state
        self.final_state = left.final_state

    def eval_cat_node(self, node):
        """Create FSA from regex cat node"""
        left = FSA(node=node.left)
        right = FSA(node=node.right)
        left.final_state.final = False
        if (right.init_state.has_incoming() and 
            left.final_state.has_outgoing()):
            left.final_state.add_transition("", right.init_state)
        else:
            left.final_state.merge(right.init_state)
        self.init_state = left.init_state
        self.final_state = right.final_state

    def eval_star_node(self, node):
        """Create FSA from regex star node"""
        child = FSA(node=node.child)
        for char, state_set in child.final_state.incoming.items():
            for state in state_set:
                state.redir_trans(char, child.final_state, child.init_state)
        self.init_state = child.init_state
        self.final_state = child.init_state
        self.init_state.final = True

    def eval_char_node(self, node):
        """Create FSA from regex character node"""
        init = State()
        final = State(final=True)
        self.init_state = init
        self.final_state = final
        init.add_transition(node.char, final)

    def eval_node(self, node):
        """Create FSA from a regex parse tree"""
        if isinstance(node, Character_Node):
            self.eval_char_node(node)

        if isinstance(node, Cat_Node):
            self.eval_cat_node(node)

        if isinstance(node, Union_Node):
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
    a = FSA(regex="abc+abd")
    print(a, "\n")
    print(a.test("abd", trace=True))

    # a = FSA(filename="a")
    # print(a)
    # print(a.test("", trace=True))

