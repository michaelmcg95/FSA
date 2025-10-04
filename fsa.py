#! /usr/bin/python3

from collections import defaultdict
import xml.etree.ElementTree as ET
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
        self.GTG_in = set()
        self.GTG_out = set()

    def merge(self, src):
        """take all transitions to/from source"""

        def change_outgoing(char, state):
            self.add_transition(char, state)
            state.incoming[char].remove(src)

        def change_incoming(char, state):
            state.add_transition(char, self)
            state.transitions[char].remove(src)

        src.iterate_over_incoming(change_incoming)
        src.iterate_over_transitions(change_outgoing)

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
    
    def make_GTG_sets(self):
        """Make sets of (Regex_Node, state) tuples for this state"""
        self.GTG_in = set()
        self.GTG_out = set()
        for char, state_set in self.transitions.items():
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

        s = f"{transitions_to_str(self.transitions):25}"
        s += f"{transitions_to_str(self.incoming)}"
        return s
    
    def __repr__(self):
        return "state " + self.label

class FSA:
    def __init__(self, regex=None, node=None, filename=None, jflap=None):
        self.final_states = set()
        if regex is not None:
            self.eval_node(parse(regex))
            self.label_states()
            
        elif node is not None:
            self.eval_node(node)
            self.label_states()

        elif filename is not None:
            self.load_file(filename)

        elif jflap is not None:
            self.load_jflap(jflap)
    
    def load_jflap(self, filename):
        """load from jflap xml file"""
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
                from_state.add_transition(char, to_state)
                
    def load_file(self, filename):
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
                self.init_state = current_state
            elif first_char == FINAL_CHAR:
                self.final_states.add(current_state)
            else:
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
                for char, state_list in state.transitions.items():
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
            # add new initial state if child init_state has an incoming transition
            if childFSA.init_state.has_incoming():
                new_init = State()
                new_init.add_transition(LAMBDA_CHAR, childFSA.init_state)
                childFSA.init_state = new_init
        self.final_states = left.final_states.union(right.final_states)
        left.init_state.merge(right.init_state)
        self.init_state = left.init_state
        if right.init_state in self.final_states:
            self.final_states.remove(right.init_state)
            self.final_states.add(left.init_state)
        self.merge_final_states()

    def merge_final_states(self):
        """Try to merge final states"""
        to_merge = []
        for fstate in self.final_states:
            # mergeable final state is not init_state and has no out transition
            if not fstate.has_outgoing() and fstate != self.init_state:
                to_merge.append(fstate)
        if len(to_merge) > 1:
            survivor = to_merge[0]
            for state in to_merge[1:]:
                survivor.merge(state)
                self.final_states.remove(state)

    def eval_cat_node(self, node):
        """Create FSA from regex cat node"""
        left = FSA(node=node.left)
        right = FSA(node=node.right)

        # merge final states of left node
        to_merge = []

        # check if left node has a single mergeable final state
        left_final = list(left.final_states)[0]
        if (len(left.final_states) == 1 and not 
            (right.init_state.has_incoming() and left_final.has_outgoing())):
            to_merge.append(left_final)
        else:
            # make final states mergeable
            for state in left.final_states:
                if state.has_outgoing():
                    new_state = State()
                    state.add_transition(LAMBDA_CHAR, new_state)
                    state = new_state
                to_merge.append(state)
        for state in to_merge:
            right.init_state.merge(state)

        # if left initial state was merged, use right initial state
        if left.init_state in to_merge:
            self.init_state = right.init_state
        else:
            self.init_state = left.init_state
        self.final_states = right.final_states

    def eval_star_node(self, node):
        """Create FSA from regex star node"""
        child = FSA(node=node.child)
        if child.init_state.has_incoming():
            self.init_state = State()
            self.init_state.add_transition(LAMBDA_CHAR, child.init_state)
        else:
            self.init_state = child.init_state
        for state in child.final_states:
            if state.has_outgoing():
                state.add_transition(LAMBDA_CHAR, self.init_state)
            else:
                self.init_state.merge(state)
        self.final_states.add(self.init_state)

    def eval_leaf_node(self, char=None):
        """Create FSA from character, lambda, or null node"""
        init = State()
        self.init_state = init
        if char == LAMBDA_CHAR:
            final = init
        else:
            final = State()
            if char != NULL_CHAR:
                init.add_transition(char, final)
        self.final_states.add(final)

    def eval_node(self, node):
        """Create FSA from a regex parse tree"""
        if isinstance(node, Character_Node):
            self.eval_leaf_node(node.char)

        elif isinstance(node, Null_Node):
            self.eval_leaf_node(NULL_CHAR)
        
        elif isinstance(node, Lambda_Node):
            self.eval_leaf_node(LAMBDA_CHAR)

        elif isinstance(node, Cat_Node):
            self.eval_cat_node(node)

        elif isinstance(node, Union_Node):
            self.eval_union_node(node)

        elif isinstance(node, Star_Node):
            self.eval_star_node(node)
    
    def GTG_init_final(self):
        """Add states so that init has no incoming transition and
        there is a single final state with no outgoing transition. 
        new states are connected only to the GTG graph."""
        self.GTG_init = State("New_Init")
        self.GTG_init.GTG_out.add((LAMBDA_NODE, self.init_state))
        self.init_state.GTG_in.add((LAMBDA_NODE, self.GTG_init))

        self.GTG_final = State("New_Final")
        for fstate in self.final_states:
            fstate.GTG_out.add((LAMBDA_NODE, self.GTG_final))
            self.GTG_final.GTG_in.add((LAMBDA_NODE, fstate))
            
    def to_regex(self):
        """Create regex accepting the same language as self"""
        states = self.get_state_list()
        for s in states:
            s.make_GTG_sets()
        self.GTG_init_final()

        while len(states) > 0:
            state = states.pop()
            state.suppress()

        init_out_nodes = [out_node for out_node, _ in self.GTG_init.GTG_out]
        parse_tree = union_all(init_out_nodes)
        return simplify(parse_tree).regex()
                    
    def test(self, s, trace=False):
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
            for next_state in state.transitions.get(char, ()):
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

if __name__ == "__main__":
    # a = FSA(regex="~")
    # a = FSA(regex="((a*(b|((c*|d)e*)*))*fg)*")
    # a = FSA(filename="a")
    # print(a)
    # print(a.to_regex())
    # print(a.to_regex())
    # print(a.test('a', trace=True))
    # print(a.test('abc', trace=True))
    # a = FSA(regex="a|(ad)")
    # print(a)
    # print(a.test("aaaeaaae", trace=True))
    # a = FSA(filename="a")
    # print(a)
    # print(a.test("bba", False))
    # print(a.to_regex())
    a = FSA(jflap="xmltest.jff")
    print(a)
    a.write_file()


