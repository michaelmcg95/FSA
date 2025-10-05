#! /usr/bin/python3

"""Converts all flap files in test_fsa directory to text transition graphs"""
import os
from fsa import FSA

file_names = [n for n in os.listdir("test_fsa") if n[-3:] == "jff"]
for file_name in file_names:
    my_fsa = FSA(jflap="testing/" + file_name)
    my_fsa.write_file(file_name[:-3] + "fsa")
