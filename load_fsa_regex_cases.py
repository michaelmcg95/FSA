import regex

# load test cases from file
# format is [(regex, {True: [cases...], False: [cases]})...]
fsa_regex_cases = []
with open("fsa_test_cases", "r") as file:
    lines = file.readlines()
regex_str = None
case_dict = {}
for line in lines:
    if line == "\n":
        fsa_regex_cases.append((regex_str, case_dict))
        case_dict = {}
    elif line[:5].lower() == "regex":
        regex_str = line.split()[1]
    else:
        expected = True if line[0].lower() == "t" else False
        cases = ["" if c == regex.LAMBDA_CHAR else c for c in line.split()[1:]]
        case_dict[expected] = cases
