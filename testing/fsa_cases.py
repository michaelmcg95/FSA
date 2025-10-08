#! /usr/bin/python3
"""Load test cases for fsa transition graph files"""

import os

TEST_CASES_DIR = "fsa_cases"

class FSA_Test_Case:
    def __init__(self, name, accept, reject):
        self.name = name
        self.accept = accept
        self.reject = reject

fsa_cases = []
os.chdir("testing")
file_names = [f[:-4] for f in os.listdir(TEST_CASES_DIR) if f[-4:] == ".fsa"]
for file_name in file_names:
    with open(f"{TEST_CASES_DIR}/{file_name}", "r") as test_strings_file:
        lines = test_strings_file.readlines()
    accept = []
    reject = []
    accepting = True
    for line in lines:
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
    fsa_cases.append(FSA_Test_Case(file_name, accept, reject))
os.chdir("..")

if __name__ == "__main__":
    for case in fsa_cases:
        print(case.name)
        print(case.accept)
        print(case.reject)