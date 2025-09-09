"""Loads regex test cases from file"""

import regex
from fsa import COMMENT_CHAR

class Regex_Test_Case:
    def __init__(self):
        self.regex = None
        self.parse_tree = None
        self.accepted = None
        self.rejected = None

fsa_regex_cases = []
with open("fsa_test_cases", "r") as file:
    lines = file.readlines()
regex_str = None
case = Regex_Test_Case()
for line in lines:
    first_char = line[0].lower()
    if first_char == COMMENT_CHAR:
        continue
    if line == "\n" and case.regex is not None:
        fsa_regex_cases.append(case)
        case = Regex_Test_Case()
    elif first_char == "r":
        case.regex = line.split(":")[1].strip()
    elif line[0].lower() == "p":
        case.parse_tree = line.split(":")[1].strip()
    else:
        words = line.split()
        test_strings = ["" if c == regex.LAMBDA_CHAR else c for c in words[1:]]
        if first_char == "t":
            case.accepted = test_strings
        else:
            case.rejected = test_strings
