#! /usr/bin/python3
"""Load test cases for fsa transition graph files"""

import os

class FSA_Test_Case:
    def __init__(self, name, accept, reject):
        self.name = name
        self.accept = accept
        self.reject = reject

fsa_cases = []
file_names = [f[:-4] for f in os.listdir("testing") if f[-4:] == ".fsa"]
for file_name in file_names:
    with open("testing/" + file_name, "r") as test_strings_file:
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

if __name__ == "__main__":
    for case in fsa_cases:
        print(case.name)
        print(case.accept)
        print(case.reject)