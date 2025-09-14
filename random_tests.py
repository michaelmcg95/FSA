#! /usr/bin/python3

import random
from regex import *
import fsa
import string

REJECT_CHAR = "X"
NUM_CASES = 5

class Parse_Tree_Generator:

    def __init__(self):
        self.chars = string.ascii_lowercase
        self.bin_node_types = [Union_Node, Cat_Node]
        self.next_char_index = 0

    def _get_next_char(self):
        result = self.chars[self.next_char_index]
        self.next_char_index += 1
        return result
    
    def _make_random_tree(self, num_leaves):
        if num_leaves == 1:
            node = Character_Node(self._get_next_char())
        elif num_leaves > 1:
            left_leaves = random.randint(1, num_leaves - 1)
            left = self._make_random_tree(left_leaves)
            right = self._make_random_tree(num_leaves - left_leaves)
            node_type = random.choice(self.bin_node_types)
            node = node_type(left, right)
        starred = random.randint(0, 10) < 3
        if starred:
            node = Star_Node(node)
        return node

    def get_random_parse_tree(self, num_leaves):
        self.next_char_index = 0
        return self._make_random_tree(num_leaves)

def strip_lambda_char(str_set):
    result = set()
    for s in str_set:
        s = s.strip(LAMBDA_CHAR)
        if s == "":
            result.add(LAMBDA_CHAR)
        else:
            result.add(s)
    return result

def make_regex_test_cases(parse_tree):
    accepted, rejected = set(), set()
    rejected.add(REJECT_CHAR)

    if isinstance(parse_tree, Character_Node):
        accepted.add(parse_tree.char)
        rejected.add(LAMBDA_CHAR)

    elif isinstance(parse_tree, Star_Node):
        child_accept, child_reject = make_regex_test_cases(parse_tree.child)
        accepted.add(LAMBDA_CHAR)
        child_accept_list = list(child_accept)
        for _ in range(min(NUM_CASES, len(child_accept))):
            accepted.add(child_accept.pop())
        for _ in range(NUM_CASES):
            cat_str = ""
            for _ in range(3):
                s = random.choice(child_accept_list)
                if s != LAMBDA_CHAR:
                    cat_str += s
            if cat_str == "":
                cat_str = LAMBDA_CHAR
            accepted.add(cat_str)
        for _ in range(min(NUM_CASES, len(child_reject))):
            test_str = child_reject.pop()
            if test_str != LAMBDA_CHAR:
                rejected.add(test_str)

    elif isinstance(parse_tree, Bin_Op_Node):
        left_accept, left_reject = make_regex_test_cases(parse_tree.left)
        right_accept, right_reject = make_regex_test_cases(parse_tree.right)
        l_accept_list = list(left_accept)
        r_accept_list = list(right_accept)
        l_reject_list = list(left_reject)
        r_reject_list = list(right_reject)

        if isinstance(parse_tree, Cat_Node):
            if LAMBDA_CHAR in left_accept.intersection(right_accept):
                accepted.add(LAMBDA_CHAR)
            else:
                rejected.add(LAMBDA_CHAR)

            for _ in range(min(NUM_CASES, len(left_accept))):
                l_str = random.choice(l_accept_list)
                r_str = random.choice(r_accept_list)
                test_str = l_str + r_str
                accepted.add(test_str)
            rejected.add(random.choice(l_accept_list) + 
                         random.choice(r_reject_list))
            rejected.add(random.choice(l_reject_list) + 
                         random.choice(r_accept_list))
            rejected.add(random.choice(l_reject_list) + 
                         random.choice(r_reject_list))

        elif isinstance(parse_tree, Union_Node):
            if LAMBDA_CHAR in left_accept.union(right_accept):
                accepted.add(LAMBDA_CHAR)
            else:
                rejected.add(LAMBDA_CHAR)

            for _ in range(min(NUM_CASES, len(left_accept))):
                accepted.add(left_accept.pop())
            for _ in range(min(NUM_CASES, len(right_accept))):
                accepted.add(right_accept.pop())
            both_reject = left_reject.intersection(right_reject)
            for _ in range(min(NUM_CASES, len(both_reject))):
                rejected.add(both_reject.pop())

    accepted = strip_lambda_char(accepted)
    rejected = strip_lambda_char(rejected)
    return accepted, rejected

def run_random_tests(tree_sizes, trees_per_size):
    tree_generator = Parse_Tree_Generator()
    failed = []
    for size in tree_sizes:
        for _ in range(trees_per_size):
            tree = tree_generator.get_random_parse_tree(size)
            test_fsa = fsa.FSA(node=simplify(tree))
            accepted, rejected = make_regex_test_cases(tree)
            regex = tree.regex()
            for case_set, expected in ((accepted, True), (rejected, False)):
                for case in case_set:
                    try:
                        if not test_fsa.test(case) == expected:
                            failed.append({"regex": regex,
                                            "tree": tree,
                                            "string": case,
                                            "expected:": expected})
                    except RecursionError:
                        print("recursion error")                      
                        print(test_fsa)
                        print(tree, regex, case, expected)

    print(f"Testing complete. {len(failed)} tests failed.")
    for failed_case in failed:
        print(failed_case)

if __name__ == "__main__":
    run_random_tests([10], 20)
    # tree_generator = Parse_Tree_Generator()
    # tree = tree_generator.get_random_parse_tree(5)
    # print(tree, tree.regex())
    # print(make_regex_test_cases(parse("(a(b+cde+f*g))*")))
