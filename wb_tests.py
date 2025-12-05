#! /usr/bin/python3

import unittest
from regex import parse
from load_regex_cases import load_regex_cases
from load_fsa_cases import make_FSA_case
from fsa import *

class Test_Regex(unittest.TestCase):
    def test_regex_parser(self):
        print("Testing regex parser")
        # test valid regexes
        with open("testing/wb_cases/regex_valid") as case_file:
            lines = case_file.readlines()
        for line in lines:
            regex, tree_str = line.split(maxsplit=1)
            tree_str = tree_str.strip()
            parse_tree = parse(regex)
            self.assertEqual(repr(parse_tree), tree_str)

        # test invalid regexes
        with open("testing/wb_cases/regex_invalid") as case_file:
            lines = case_file.readlines()
        for line in lines:
            self.assertRaises(SyntaxError, lambda : parse(line.strip()))

    def test_nfa_regex(self):
        print("Testing conversion between regex and nfa ")
        # test conversion between regex and nfa
        cases = load_regex_cases("testing/wb_cases/nfa_from_regex")
        for case in cases:
            test_nfa = NFA(regex=case.regex)
            # convert to regex and back to nfa
            test_nfa2 = NFA(regex=test_nfa.to_regex())
            num_states = len(test_nfa.get_state_list())
            self.assertEqual(case.num_states, num_states)
            for s in case.accepted:
                self.assertTrue(test_nfa.test(s))
                self.assertTrue(test_nfa2.test(s))
            for s in case.rejected:
                self.assertFalse(test_nfa.test(s))
                self.assertFalse(test_nfa2.test(s))

    def test_nfa_test(self):
        print("Testing nfa string acceptance")
        # test nfa string acceptance
        case = make_FSA_case("testing/wb_cases/nfa_test")
        test_nfa = NFA(jflap=f"{case.path}.jff")
        for test_string in case.accept:
            msg = f"{case.path} rejected {test_string}"
            self.assertTrue(test_nfa.test(test_string), msg)
            self.assertTrue(test_nfa.test_backtrack(test_string), msg + " backtrack")

        for test_string in case.reject:
            msg = f"{case.path} accepted {test_string}"
            self.assertFalse(test_nfa.test(test_string), msg)
            self.assertFalse(test_nfa.test_backtrack(test_string), msg + " backtrack")
        
    def test_dfa(self):
        print("Testing dfa string acceptance")
        # test dfa string acceptance
        case = make_FSA_case("testing/wb_cases/dfa_test")
        test_dfa = DFA(jflap=case.path + ".jff")
        for test_string in case.accept:
            msg = f"{case.path} rejected {test_string}"
            self.assertTrue(test_dfa.test(test_string), msg)

        for test_string in case.reject:
            msg = f"{case.path} accepted {test_string}"
            self.assertFalse(test_dfa.test(test_string), msg)

    def test_nfa_to_dfa(self):
        print("Testing nfa to dfa conversion")
        # test nfa to dfa conversion
        case = make_FSA_case("testing/wb_cases/nfa_to_dfa")
        test_dfa = DFA(nfa=NFA(jflap=case.path + ".jff"))
        for test_string in case.accept:
            msg = f"{case.path} rejected {test_string}"
            self.assertTrue(test_dfa.test(test_string), msg)

        for test_string in case.reject:
            msg = f"{case.path} accepted {test_string}"
            self.assertFalse(test_dfa.test(test_string), msg)

    def test_reduce_dfa(self):
        print("Testing dfa state reduction")
        # test dfa state reduction method
        case = make_FSA_case("testing/wb_cases/reduce_dfa")
        test_dfa = DFA(jflap=case.path + ".jff").reduce()
        for test_string in case.accept:
            msg = f"{case.path} rejected {test_string}"
            self.assertTrue(test_dfa.test(test_string), msg)

        for test_string in case.reject:
            msg = f"{case.path} accepted {test_string}"
            self.assertFalse(test_dfa.test(test_string), msg)

    def test_is_dfa(self):
        print("Testing dfa identification")
        tg = Transition_Graph(jflap="testing/wb_cases/is_dfa_yes.jff")
        self.assertTrue(tg.is_dfa())
        tg = Transition_Graph(jflap="testing/wb_cases/is_dfa_no_mult.jff")
        self.assertFalse(tg.is_dfa())
        tg = Transition_Graph(jflap="testing/wb_cases/is_dfa_no_lambda.jff")
        self.assertFalse(tg.is_dfa())
    

if __name__ == "__main__":
    unittest.main()