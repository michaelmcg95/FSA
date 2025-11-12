#! /usr/bin/python3

from collections import defaultdict
import xml.etree.ElementTree as ET
from regex import *

LABEL_CHAR = "@"
COMMENT_CHAR = "#"
START_CHAR = "!"
FINAL_CHAR = "*"

class FSA_Error(Exception):
    pass

class Transition_Graph:
    """Read FSA data file and construct transition graph"""
    def __init__(self, filename=None, jflap=None):
        self.init_state_label = None
        self.final_state_labels = set()
        self.state_dict = {}
        self.transition_chars = set()

        if filename:
            self.load_file(filename)
        elif jflap:
            self.load_jflap(jflap)

        if self.init_state_label is None:
            raise FSA_Error("No initial state")
        if len(self.final_state_labels) == 0:
            raise FSA_Error("No final state")

        self.is_dfa = self.check_if_dfa()

    def get_state_dict(self):
        return self.state_dict
    
    def load_file(self, filename):
        with open(filename, "r") as file:
            lines = file.readlines()

        lines_words = [l.split() for l in lines if l[0] != COMMENT_CHAR]
        lines_words = [words for words in lines_words if len(words) > 0]

        current_state_label = None
        for words in lines_words:
            first_char = words[0][0]
            if first_char == LABEL_CHAR:
                current_state_label = words[0][1:]
                if current_state_label == "":
                    raise SyntaxError("Missing state label")
                self.state_dict[current_state_label] = defaultdict(list)
            elif first_char == START_CHAR:
                if self.init_state_label is not None:
                    raise SyntaxError("Multiple initial states")
                self.init_state_label = current_state_label
            elif first_char == FINAL_CHAR:
                self.final_state_labels.add(current_state_label)
            else:
                self.state_dict[current_state_label][first_char] += words[1:]
                self.transition_chars.add(first_char)
  
    def load_jflap(self, filename):
        """load from jflap xml file"""
        tree = ET.parse(filename)
        automaton = tree.find("automaton")
        for elem in automaton:
            if elem.tag == "state":
                label = elem.attrib["id"]
                self.state_dict[label] = defaultdict(list)
                if elem.find("initial") is not None:
                    self.init_state_label = label
                if elem.find("final") is not None:
                    self.final_state_labels.add(label)
            elif elem.tag == "transition":
                char = elem.find("read").text
                if char is None:
                    char = LAMBDA_CHAR
                from_label = elem.find("from").text
                to_label = elem.find("to").text
                if from_label not in self.state_dict:
                    self.state_dict[from_label] = defaultdict(list)
                    self.transition_chars.add(char)
                self.state_dict[from_label][char].append(to_label)
         
        
    def check_if_dfa(self):
        if LAMBDA_CHAR in self.transition_chars:
            return False
        for transitions in self.state_dict.values():
            if self.transition_chars - set(transitions.keys()):
                return False
        return True


class State:
    def __init__(self, label=""):
        self.label = label

    def __repr__(self):
        return self.label
    
class NFA_State(State):
    def __init__(self, *args, **kwargs):
        self.outgoing = defaultdict(set)
        self.incoming = defaultdict(set)
        self.GTG_in = set()
        self.GTG_out = set()
        super().__init__(*args, **kwargs)

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

    def find_all_reachable(self, char, visited=None):
        """Get all states reachable by consuming char"""
        if visited is None:
            visited = set()
        # prevent infinite recursion on lambda cycles
        if self in visited:
            return set()
        
        states = set()
        if char == LAMBDA_CHAR:
            states.add(self)
        
        # try transitions on char
        if char != LAMBDA_CHAR:
            for next_state in self.outgoing[char]:
                states |= next_state.find_all_reachable(LAMBDA_CHAR)

        # try lambda-transitions
        visited.add(self)
        for next_state in self.outgoing[LAMBDA_CHAR]:
            states |= next_state.find_all_reachable(char, visited)

        return states

    def add_transition(self, char, state):
        self.outgoing[char].add(state)
        state.incoming[char].add(self)

    def has_outgoing(self):
        return len(self.outgoing) != 0
    
    def has_incoming(self):
        return len(self.incoming) != 0
    
    def iterate_over_outgoing(self, func):
        return NFA_State._iterate_over(func, self.outgoing)
    
    def iterate_over_incoming(self, func):
        return NFA_State._iterate_over(func, self.incoming)
    
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
        """Convert outgoing transitions to string"""
        s = ""
        for char, states in self.outgoing.items():
            s += f"{char}: [{', '.join([s.label for s in states])}], "
        return s[:-2]
    
class DFA_State(State):
    def __init__(self, *args, **kwargs):
        self.transitions = {}
        super().__init__(*args, **kwargs)

    def __str__(self):
        s = ""
        for char, state in self.transitions.items():
            s += f"{char}: {repr(state)}, "
        return s[:-2]
    
    def add_transition(self, char, state):
        self.transitions[char] = state

class FSA:
    def __repr__(self):
        s = f"if {'Label':15}{'Transitions'}\n{"-"*70}\n"
        for state in self.get_state_list():
            state_type = START_CHAR if state == self.init_state else "-"
            state_type += FINAL_CHAR if state in self.final_states else "-"
            s += f"{state_type} {repr(state):15}{str(state)}\n"
        
        return s 

class NFA(FSA):
    def __init__(self, regex=None, node=None, filename=None, jflap=None, tg=None):
        self.init_state = None
        self.final_states = set()

        if jflap is not None:
            tg = Transition_Graph(jflap=jflap)

        if filename is not None:
            tg = Transition_Graph(filename=filename)

        if tg is not None:
            self.load_from_transition_graph(tg)

        if regex is not None:
            self.eval_node(parse(regex))
            self.label_states()
            
        elif node is not None:
            self.eval_node(node)
            self.label_states()
    
    def load_from_transition_graph(self, transition_graph):
        """Construct nfa from transition graph"""
        transition_dict = transition_graph.get_state_dict()
        state_dict = {label: NFA_State(label) 
                      for label in transition_dict.keys()}
        for label, transitions in transition_dict.items():
            state = state_dict[label]
            if label == transition_graph.init_state_label:
                self.init_state = state
            if label in transition_graph.final_state_labels:
                self.final_states.add(state)
            for char, labels in transitions.items():
                for dest_label in labels:
                    state.add_transition(char, state_dict[dest_label])

    def label_states(self):
        for count, state in enumerate(self.get_state_list()):
            state.label = str(count)

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
                file.write("\n")

    def write_jflap(self):
        x = 100
        y = 150
        states = self.get_state_list()
        tree = ET.ElementTree(ET.Element("structure"))
        id_dict = {s: str(i) for i, s in enumerate(states)}
        root = tree.getroot()
        ET.SubElement(root, "type").text = "fa"
        automaton = ET.SubElement(root, "automaton")
        for state, id in id_dict.items():
            attrib = {"id": id, "name": state.label}
            state_elem = ET.SubElement(automaton, "state", attrib=attrib)
            ET.SubElement(state_elem, "x").text = str(x)
            ET.SubElement(state_elem, "y").text = str(y)
            if state in self.final_states:
                ET.SubElement(state_elem, "final")
            if state == self.init_state:
                ET.SubElement(state_elem, "initial")
            x += 70

        for state in states:
            for char, dest_states in state.outgoing.items():
                if char == LAMBDA_CHAR:
                    char = ""
                for dest in dest_states:
                    trans = ET.SubElement(automaton, "transition")
                    ET.SubElement(trans, "from").text = id_dict[state]
                    ET.SubElement(trans, "to").text = id_dict[dest]
                    ET.SubElement(trans, "read").text = char
                    

        # print(ET.tostringlist(root, encoding='unicode'))
        ET.indent(root)

        with open("xmltest", "w") as file:
            tree.write(file, encoding="unicode", xml_declaration=True)


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
        
    def eval_union_node(self, node):
        """Create FSA from regex union node"""
        left = NFA(node=node.left)
        right = NFA(node=node.right)
        for childFSA in left, right:
            # add new initial state if child init_state has an incoming transition
            if childFSA.init_state.has_incoming():
                new_init = NFA_State()
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
        left = NFA(node=node.left)
        right = NFA(node=node.right)

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
                    new_state = NFA_State()
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
        child = NFA(node=node.child)
        if child.init_state.has_incoming():
            self.init_state = NFA_State()
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
        init = NFA_State()
        self.init_state = init
        if char == LAMBDA_CHAR:
            final = init
        else:
            final = NFA_State()
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
        self.GTG_init = NFA_State("New_Init")
        self.GTG_init.GTG_out.add((LAMBDA_NODE, self.init_state))
        self.init_state.GTG_in.add((LAMBDA_NODE, self.GTG_init))

        self.GTG_final = NFA_State("New_Final")
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
    
    def get_alphabet(self):
        """Get set of characters consumed in transitions"""
        states = self.get_state_list()
        alph =  reduce(set.union, [set(s.outgoing.keys()) for s in states], set())
        return alph - {LAMBDA_CHAR}    
    
class DFA(FSA):
    def __init__(self, nfa=None, transition_graph=None):
        self.init_state = None
        self.final_states = set()
        if transition_graph:
            self.load_from_transition_graph(transition_graph)
        if nfa:
            self.convert_from_NFA(nfa)

    def load_from_transition_graph(self, transition_graph):
        """Construct dfa from transition graph"""
        transition_dict = transition_graph.get_state_dict()
        state_dict = {label: DFA_State(label) 
                      for label in transition_dict.keys()}
        for label, transitions in transition_dict.items():
            state = state_dict[label]
            if label == transition_graph.init_state_label:
                self.init_state = state
            if label in transition_graph.final_state_labels:
                self.final_states.add(state)
            for char, labels in transitions.items():
                state.add_transition(char, state_dict[labels[0]])

    def convert_from_NFA(self, nfa):
        """Construct dfa from nfa"""
        alphabet = nfa.get_alphabet()
        complete = {}
        pending = {}
        init_states = nfa.init_state.find_all_reachable(LAMBDA_CHAR)
        self.init_state = DFA_State(str(init_states))
        pending[frozenset(init_states)] = self.init_state
        while pending:
            label, state = pending.popitem()
            for char in alphabet:
                reachable_states = set()
                for nfa_state in label:
                    reachable_states |= nfa_state.find_all_reachable(char)
                # freeze reachable_states to make it hashable
                reachable_states = frozenset(reachable_states)
                if label == reachable_states:
                    state.add_transition(char, state)
                elif reachable_states in complete:
                    state.add_transition(char, complete[reachable_states])
                elif reachable_states in pending:
                    state.add_transition(char, pending[reachable_states])
                else:
                    new_label = '{}'
                    if reachable_states:
                        new_label = str(set(reachable_states))
                    new_state = DFA_State(new_label)
                    pending[reachable_states] = new_state
                    state.add_transition(char, new_state)
            complete[label] = state
        
        self.final_states = {state for nfa_states, state in complete.items()
                             if nfa_states.intersection(nfa.final_states)}
        
    def test(self, s, trace=False):
        """Test if DFA accepts a string"""
        def print_trace(state, char, rem_str):
            print(f"{state.label:<13}{char:15}{rem_str}")

        if trace:
            print("State         Character      Remaining String")
            print("-" * 50)
            print_trace(self.init_state, "(start)", s)

        state = self.init_state
        for i, char in enumerate(s, 1):
            state = state.transitions[char]
            if trace:
                print_trace(state, char, s[i:])
        accepted = state in self.final_states
        if trace:
            if accepted:
                print(f"{s} accepted")
            else:
                print(f"{s} rejected")
        return accepted
    
    def reduce(self):
        """Minimize number of states"""
        
        new_dfa = DFA()
        alphabet = self.init_state.transitions.keys()
        states = self.get_state_list()

        final_states = self.final_states.copy()
        nonfinal_states = set(states) - final_states
        state_eq_classes = {s: nonfinal_states for s in nonfinal_states}
        for s in final_states:
            state_eq_classes[s] = final_states

        equiv_classes = [final_states, nonfinal_states]
        marked_new_pair = True

        def distinguishable(s1, s2):
            """test if states are distinguishable, given current partitions"""
            for char in alphabet:
                s1_next = s1.transitions[char]
                s2_next = s2.transitions[char]
                if state_eq_classes[s1_next] != state_eq_classes[s2_next]:
                    return True
            return False

        # continue until no new partitions are created
        while marked_new_pair:
            new_equiv_classes = []
            for eq_class in equiv_classes:
                if len(eq_class) == 1:
                    continue

                eq_class_iter = iter(eq_class)
                # select partition element
                partition_elem = next(eq_class_iter)
                distingiushed_states = set()

                # find distinguishable elements
                for elem in eq_class_iter:
                    if distinguishable(elem, partition_elem):
                        distingiushed_states.add(elem)    

                # move distinguishable elements to new set
                if distingiushed_states:
                    eq_class -= distingiushed_states
                    new_equiv_classes.append(distingiushed_states)
                    for s in distingiushed_states:
                        state_eq_classes[s] = distingiushed_states

            if new_equiv_classes:
                equiv_classes += new_equiv_classes
            else:
                marked_new_pair = False

        # create new state for each equivalence class
        new_states_dict = {}
        for eq_set in equiv_classes:
            label = "".join([s.label for s in eq_set])
            new_states_dict[frozenset(eq_set)] = DFA_State(label=label)

        # create the initial state
        new_init_state_set = frozenset(state_eq_classes[self.init_state])
        new_dfa.init_state = new_states_dict[new_init_state_set]

        # set up the transition graph
        for eq_set, new_state in new_states_dict.items():
            # check for final states
            if eq_set.intersection(self.final_states):
                new_dfa.final_states.add(new_state)

            # pick an arbitrary member of the equivalence class
            old_state = next(iter(eq_set))
            for char in alphabet:
                old_next = old_state.transitions[char]
                next_state_set = frozenset(state_eq_classes[old_next])
                new_state.add_transition(char, new_states_dict[next_state_set])

        return new_dfa
    
    def get_state_list(self):
        """Get list of reachable states in DFS traversal order."""
        state_list = []
        to_visit = [self.init_state]
        visited = set()

        while len(to_visit) > 0:
            state = to_visit.pop()
            if state not in visited:
                visited.add(state)
                for next_state in state.transitions.values():
                    to_visit.append(next_state)
                state_list.append(state)
        return state_list

    def __repr__(self):
        s = f"if {'Label':15}{'Transitions'}\n{"-"*70}\n"
        for state in self.get_state_list():
            state_type = START_CHAR if state == self.init_state else "-"
            state_type += FINAL_CHAR if state in self.final_states else "-"
            s += f"{state_type} {repr(state):15}{state}\n"
        
        return s 

if __name__ == "__main__":
    # tg = Transition_Graph(jflap="testing/fsa_cases/choices.jff")
    # n = NFA(transition_graph=tg)
    # print(n)
    # nfa = NFA(filename='reduce_test')
    # dfa = DFA(nfa=nfa)
    # print(dfa)
    # dfa = dfa.reduce()
    # print(dfa)
    # print(dfa.test("100001", True))
    # print(a.init_state.find_all_reachable('a'))
    a = NFA(filename="a")
    # print(a.to_regex())
    # print(a.to_regex())
    # print(a.test('a', trace=True))
    # print(a.test('abc', trace=True))
    # a = NFA(regex="a|(ad)|ab")
    # print(a)
    # d = DFA(nfa = a)
    # print(d)
    # print(d.reduce())
    # print(a.test("aaaeaaae", trace=True))
    # a = NFA(filename="a")
    # print(a)
    # print(a.test("bba", False))
    # print(a.to_regex())
    # a = NFA(jflap="testing/fsa_cases/lambda_cycles.jff")
    a.write_jflap()
    # a.write_file()
