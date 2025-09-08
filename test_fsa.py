#! /usr/bin/python3

import unittest
import fsa
import regex
from load_fsa_regex_cases import fsa_regex_cases

class Test_FSA_from_regex(unittest.TestCase):
    def test_fsa(self):
        for regex_str, case_dict in fsa_regex_cases:
            for expected, cases in case_dict.items():
                for case in cases:
                    wrong_action = "accepted"
                    if expected:
                        wrong_action = "rejected"
                    msg = f"{regex_str} {wrong_action} {case}"
                    self.assertEqual(expected,
                                     fsa.FSA(regex=regex_str).test(case), msg)

if __name__ == "__main__":
    unittest.main()
