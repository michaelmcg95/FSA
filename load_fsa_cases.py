#! /usr/bin/python3
"""Load test cases for fsa transition graph files"""

import os

class FSA_Test_Case:
    def __init__(self, path, accept, reject):
        self.path = path
        self.accept = accept
        self.reject = reject

def make_FSA_case(path):
    with open(path, "r") as test_strings_file:
        lines = test_strings_file.readlines()
    accept = []
    reject = []
    accepting = True
    for line in lines:
        if line[0] == "#":
            continue
        line = line.strip()
        if len(line) < 1 or line.lower() == "accept":
            continue
        elif line.lower() == "reject":
            accepting = False
        else:
            if accepting:
                accept.append(line)
            else:
                reject.append(line)
    return FSA_Test_Case(path, accept, reject)


def load_fsa_cases(dir):
    fsa_cases = []
    file_names = [f[:-4] for f in os.listdir(dir) if f[-4:] == ".jff"]
    for file_name in file_names:
        fsa_cases.append(make_FSA_case(f"{dir}/{file_name}"))
    return fsa_cases

if __name__ == "__main__":
    fsa_cases = load_fsa_cases("testing/fsa_cases")
    for case in fsa_cases:
        print(case.path)
        print(case.accept)
        print(case.reject)