#! /usr/bin/python3

"""Test suite for fsa.py"""

import unittest
import regex
import os
from fsa import *
from testing.fsa_cases import fsa_cases
from testing.fsa_regex_cases import fsa_regex_cases

SUCCESS_MSG = "\nAll tests passed"

def print_test_desc(test_desc):
    print("\n" + "*" * 80)
    print(test_desc)
    print("*" * 80)

class Test_FSA_From_File(unittest.TestCase):
    def test_fsa(self):
        print_test_desc("Testing valid transition graph files")
        for case in fsa_cases:
            print(case.name)
            test_nfa = NFA(filename=f"testing/fsa_cases/{case.name}.fsa")
            test_dfa = DFA(nfa = test_nfa).reduce()
            for test_string in case.accept:
                msg = f"{case.name} rejected {test_string}"
                self.assertTrue(test_nfa.test(test_string), msg)
                self.assertTrue(test_nfa.test_simultaneous(test_string), msg + " simult")
                self.assertTrue(test_dfa.test(test_string), msg)

            for test_string in case.reject:
                msg = f"{case.name} accepted {test_string}"
                self.assertFalse(test_nfa.test(test_string), msg)
                self.assertFalse(test_nfa.test_simultaneous(test_string), msg + " simult")
                self.assertFalse(test_dfa.test(test_string), msg)
        print(SUCCESS_MSG)

    def test_fsa_errors(self):
        print_test_desc("Testing invalid transition graph files")
        file_names = os.listdir("testing/fsa_errors")
        paths = ["testing/fsa_errors/" + name for name in file_names]
        for path in paths:
            print(path)
            self.assertRaises(FSA_Error, lambda : NFA(filename=path))
        print(SUCCESS_MSG)


class Test_FSA_From_Regex(unittest.TestCase):
    """Test fsa created from regex string"""
    def test_fsa_regex(self):
        print_test_desc("Testing valid regexes")
        for case in fsa_regex_cases:
            print(case.regex)
            test_nfa = NFA(regex=case.regex)
            test_dfa = DFA(nfa=test_nfa).reduce()
            round_trip_fsa = NFA(regex=test_nfa.to_regex())
            for test_string in case.accepted:
                msg = f"{case.regex} rejected {test_string}"
                self.assertTrue(test_nfa.test(test_string), "NFA for " + msg)
                self.assertTrue(test_nfa.test_simultaneous(test_string), msg + " simult")
                self.assertTrue(test_dfa.test(test_string), "DFA for " + msg)
                rt_msg = "NFA->regex->NFA for " + msg
                self.assertTrue(round_trip_fsa.test(test_string), rt_msg)
            for test_string in case.rejected:
                msg = f"{case.regex} accepted {test_string}"
                self.assertFalse(test_nfa.test(test_string), "NFA for " + msg)
                self.assertFalse(test_nfa.test_simultaneous(test_string), msg + " simult")
                self.assertFalse(test_dfa.test(test_string), "DFA for " + msg)
                rt_msg = "NFA->regex->NFA for " + msg
                self.assertFalse(round_trip_fsa.test(test_string), rt_msg)
            self.assertEqual(repr(regex.parse(case.regex)), case.parse_tree)
        print(SUCCESS_MSG)
    
    def test_syntax_err(self):
        print_test_desc("Testing invalid regexes")
        with open("testing/regex_syntax_errors", "r") as file:
            lines = file.readlines()
        for line in lines:
            # remove newline
            line = line[:-1]
            print(line)
            self.assertRaises(SyntaxError, lambda: regex.parse(line))
        print(SUCCESS_MSG)

if __name__ == "__main__":
    unittest.main()
