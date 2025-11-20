"""Loads regex test cases from file"""

from fsa import COMMENT_CHAR

class Regex_Test_Case:
    def __init__(self, regex):
        self.regex = regex
        self.parse_tree = None
        self.accepted = None
        self.rejected = None
        self.num_states = None
    
    def is_complete(self):
        return all((self.regex, self.parse_tree,
                    self.accepted is not None, self.rejected is not None))

def load_regex_cases(filename):
    """Load all regex test cases from file"""
    cases = []

    with open(filename, "r") as file:
        lines = file.readlines()

    case = None
    for line in lines:
        descriptor = line[0].lower()
        # skip empty lines and comment
        if descriptor in ['-', '\n', COMMENT_CHAR]:
            continue
        line_value = line.split(":")[1].strip()
        line_words = line_value.split()
        # start of new case
        if descriptor == "r":
            if case:
                cases.append(case)
            case = Regex_Test_Case(regex=line_value)
        elif descriptor == "p":
            case.parse_tree = line_value
        elif descriptor == "n":
            case.num_states = int(line_words[0])
        else:
            if descriptor == "t":
                case.accepted = line_words
            elif descriptor == "f":
                case.rejected = line_words
    if case:
        cases.append(case)
    return cases

