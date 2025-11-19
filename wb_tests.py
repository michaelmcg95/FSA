#! /usr/bin/python3

import unittest
from regex import parse

class Test_Regex(unittest.TestCase):
    def test_valid(self):
        with open("testing/wb_cases/valid") as case_file:
            lines = case_file.readlines()
        for line in lines:
            regex, tree_str = line.split(maxsplit=1)
            tree_str = tree_str.strip()
            parse_tree = parse(regex)
            self.assertEqual(repr(parse_tree), tree_str)

    def test_invalid(self):
        with open("testing/wb_cases/invalid") as case_file:
            lines = case_file.readlines()
        for line in lines:
            self.assertRaises(SyntaxError, lambda : parse(line.strip()))

if __name__ == "__main__":
    unittest.main()