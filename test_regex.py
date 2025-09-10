#! /usr/bin/python3

"""Test suite for regex.py"""

import unittest
import regex

class Test_Parser_Syntax_Errors(unittest.TestCase):
    """Test fsa created from regex string"""
    def test_syntax_err(self):
        with open("regex_syntax_errors", "r") as file:
            lines = file.readlines()
        for line in lines:
            # remove newline
            line = line[:-1]
            self.assertRaises(SyntaxError, lambda: regex.parse(line))

if __name__ == "__main__":
    unittest.main()