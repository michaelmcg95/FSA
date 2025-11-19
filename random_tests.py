#! /usr/bin/python3

import random
from regex import *
from fsa import NFA
import string
import unittest

ALPHABET_SIZE = 4
MAX_LENGTH = 6
NUM_LETTERS = 4
NUM_TESTS = 20

class Regex_Case:
    def __init__(self, tree, accepted, rejected):
        self.tree = tree
        self.regex = tree.regex()
        self.accepted = accepted
        self.rejected = rejected

class Regex_Case_Generator:
    """Generate random regex test cases"""
    def __init__(self, alphabet_size, max_len):
        self.alphabet = string.ascii_lowercase[:alphabet_size]
        self.max_len = max_len
        self.bin_node_types = [Union_Node, Cat_Node]   
        self.all_strings = [""]
        prev_len_strings = self.all_strings
        for i in range(0, max_len):
            new_strings = []
            for char in self.alphabet:
                new_strings += [s + char for s in prev_len_strings]
            self.all_strings += (new_strings)
            prev_len_strings = new_strings
        self.all_strings = set(self.all_strings)

    def generate(self, num_letters=NUM_LETTERS):
        """Generate a random test case"""
        tree = self._make_random_tree(num_letters)
        return self._make_regex_test_case(tree)
    
    def _make_random_tree(self, num_leaves, lambda_ok=False):
        """Make a random regex parse tree"""
        if num_leaves == 1:
            if lambda_ok and random.randint(0, 3) == 0:
                node = LAMBDA_NODE
            else:
                node = CHAR_NODES[random.choice(self.alphabet)]
        else:
            left_leaves = random.randint(1, num_leaves - 1)
            node_type = random.choice(self.bin_node_types)
            lambda_ok = node_type == Union_Node
            left = self._make_random_tree(left_leaves, lambda_ok)
            right = self._make_random_tree(num_leaves - left_leaves, lambda_ok)
            node = node_type(left, right)
        if random.randint(0, 9) < 2:
            node = Star_Node(node)
        return node

    def _make_regex_test_case(self, parse_tree):
        """Generate accepted and rejected strings from a regex parse tree"""
        accepted = set()

        if isinstance(parse_tree, Character_Node):
            accepted.add(parse_tree.char)

        elif parse_tree == LAMBDA_NODE:
            accepted.add("")

        elif isinstance(parse_tree, Star_Node):
            accepted.add("")
            child_test_case = self._make_regex_test_case(parse_tree.child)
            child_accept =  child_test_case.accepted - {""}
            new_concats = child_accept
            while new_concats:
                accepted |= new_concats
                prev_concats = new_concats
                new_concats = set()
                for concat_string in prev_concats:
                    for s in child_accept:
                        new_string = concat_string + s
                        if len(new_string) <= self.max_len:
                            new_concats.add(new_string)

        elif isinstance(parse_tree, Bin_Op_Node):
            left_accepted = self._make_regex_test_case(parse_tree.left).accepted
            right_accepted = self._make_regex_test_case(parse_tree.right).accepted

            if isinstance(parse_tree, Cat_Node):
                for left_str in left_accepted:
                    for right_str in right_accepted:
                        new_string = left_str + right_str
                        if len(new_string) <= self.max_len:
                            accepted.add(new_string)

            elif isinstance(parse_tree, Union_Node):
                accepted = left_accepted | right_accepted

        rejected = self.all_strings - accepted
        return Regex_Case(parse_tree, accepted, rejected)

class Test_Random_Regex(unittest.TestCase):
    def test(self):
        case_generator = Regex_Case_Generator(ALPHABET_SIZE, MAX_LENGTH)
        for _ in range(NUM_TESTS):
            test_case = case_generator.generate()
            print("Testing " + test_case.regex)
            nfa = NFA(node=test_case.tree)
            msg = test_case.regex + " rejected "
            for s in test_case.accepted:
                self.assertTrue(nfa.test(s), msg + s)
            msg = test_case.regex + " accepted "
            for s in test_case.rejected:
                self.assertFalse(nfa.test(s), msg + s)

if __name__ == "__main__":
    unittest.main()
    # g = Regex_Case_Generator(4, 6)
    # for _ in range(20):
    #     c = g.generate()
    #     print(c.regex)
