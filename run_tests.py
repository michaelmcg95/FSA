#! /usr/bin/python3

"""Test suite for fsa.py"""

import unittest
import regex
import os
from fsa import FSA
from testing.fsa_cases import fsa_cases
from testing.fsa_regex_cases import fsa_regex_cases

class Test_FSA_From_File(unittest.TestCase):
    def test_fsa(self):
        for case in fsa_cases:
            test_fsa = FSA(filename=f"testing/fsa_cases/{case.name}.fsa")
            for test_string in case.accept:
                msg = f"{case.name} rejected {test_string}"
                self.assertTrue(test_fsa.test(test_string), msg)
            for test_string in case.reject:
                msg = f"{case.name} accepted {test_string}"
                self.assertFalse(test_fsa.test(test_string), msg)

    def test_fsa_errors(self):
        file_names = os.listdir("testing/fsa_errors")
        paths = ["testing/fsa_errors/" + name for name in file_names]
        for path in paths:
            self.assertRaises(SyntaxError, lambda : FSA(filename=path))


class Test_FSA_From_Regex(unittest.TestCase):
    """Test fsa created from regex string"""
    def test_fsa_regex(self):
        for case in fsa_regex_cases:
            test_fsa = FSA(regex=case.regex)
            round_trip_fsa = FSA(regex=test_fsa.to_regex())
            for test_string in case.accepted:
                msg = f"{case.regex} rejected {test_string}"
                self.assertTrue(test_fsa.test(test_string), msg)
                rt_msg = "FSA->regex->FSA " + msg
                self.assertTrue(round_trip_fsa.test(test_string), rt_msg)
            for test_string in case.rejected:
                msg = f"{case.regex} accepted {test_string}"
                self.assertFalse(test_fsa.test(test_string), msg)
                rt_msg = "FSA->regex->FSA " + msg
                self.assertFalse(round_trip_fsa.test(test_string), rt_msg)
            self.assertEqual(repr(regex.parse(case.regex)), case.parse_tree)
    
    def test_syntax_err(self):
        with open("testing/regex_syntax_errors", "r") as file:
            lines = file.readlines()
        for line in lines:
            # remove newline
            line = line[:-1]
            self.assertRaises(SyntaxError, lambda: regex.parse(line))

if __name__ == "__main__":
    unittest.main()
