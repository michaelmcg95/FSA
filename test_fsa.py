#! /usr/bin/python3

"""Test suite for fsa.py"""

import unittest
import fsa
import regex
from load_fsa_regex_cases import fsa_regex_cases

class Test_FSA_from_regex(unittest.TestCase):
    """Test fsa created from regex string"""
    def test_fsa(self):
        for case in fsa_regex_cases:
            test_fsa = fsa.FSA(regex=case.regex)
            for test_string in case.accepted:
                msg = f"{case.regex} rejected {test_string}"
                self.assertTrue(test_fsa.test(test_string), msg)
            for test_string in case.rejected:
                msg = f"{case.regex} accepted {test_string}"
                self.assertFalse(test_fsa.test(test_string), msg)
            self.assertEqual(repr(regex.parse(case.regex)), case.parse_tree)

if __name__ == "__main__":
    unittest.main()
