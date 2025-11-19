"""Loads regex test cases from file"""

from fsa import COMMENT_CHAR

class Regex_Test_Case:
    def __init__(self, regex):
        self.regex = regex
        self.parse_tree = None
        self.accepted = None
        self.rejected = None
    
    def is_complete(self):
        return all((self.regex, self.parse_tree,
                    self.accepted is not None, self.rejected is not None))

def load_regex_cases(filename):
    cases = []

    with open(filename, "r") as file:
        lines = file.readlines()

    case = None
    for line in lines:
        first_char = line[0].lower()
        # skip empty lines and comment
        if first_char in ['-', '\n', COMMENT_CHAR]:
            continue
        # start of new case
        elif first_char == "r":
            if case:
                cases.append(case)
            case = Regex_Test_Case(line.split(":")[1].strip())
        elif line[0].lower() == "p":
            case.parse_tree = line.split(":")[1].strip()
        else:
            words = line.split()
            test_strings = words[1:]
            if first_char == "t":
                case.accepted = test_strings
            elif first_char == "f":
                case.rejected = test_strings
    if case:
        cases.append(case)
    return cases

