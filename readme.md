# Finite State Automata Simulator
By Michael McGuan

mcguanm@oregonstate.edu

For CS406 Fall 2025

Supervisor: Tim Alcon

## Table of Contents

[Summary](#summary)

[Quick Start Guide](#quick-start-guide)

[Commands](#commands)
* [help](#help)
* [quit](#quit)
* [load](#load)
* [test](#test)
* [batch](#batch)
* [trace](#trace)
* [print](#print)
* [write](#write)
* [regex](#regex)
* [import](#import)
* [export](#export)
* [reduce](#reduce)
* [dfa](#dfa)
* [type](#type)
* [label](#label)

[File Format](#file-format)

[Regex Format](#regex-format)

## Summary

This program simulates the operation of finite state autamata (FSA). It supports both deterministic finite state automata (DFA)
and nondeterministic finite state automata (NFA). The user can create an automaton by loading a text file containing a description of the automaton's states and transitions.
In addition to plain text format, the program supports importing and exporting JFLAP xml files. Automata created from files are loaded as DFAs if they meet the requirements,
otherwise they are loaded as NFAs. All regexes are loaded as NFAs. Most functions are available to both types of automata, but certain functions are only available for one type or the other.
Alternatively, the user can input a regular expression (regex) and convert it to an equivalent NFA. Once an automaton is constructed, the user can test
strings to see if the automaton accepts them. The program allows the user to print a text description of the automaton's transition graph and save it to a file.
The user can also generate an equivalent regex from an automaton.



## Quick Start Guide
The first thing to do is to create an automaton. You can do this by loading one of the demo files.
```
> load demo
```
To see what this automaton does, you can print its transition diagram.
```
> print
```
Here is the output:
```
if Label          Transitions
----------------------------------------------------------------------
!- 0              a: [0], b: [1]
-* 1
```
This is telling us there are two states labeled 0 and 1. 0 is the initial state and 1 is a final state.
From state 0, we can transition back to 0 on 'a' and to 1 on 'b'. This NFA corresponds to the regex a*b.

Now we can test strings.
```
> test a
reject
> test b
accept
> test aaab
accept
> test ^
reject
```
The last test '^' is a special character representing the empty string.

To, generate the equivelent regex from this NFA, use the regex command.
```
> regex
a*b
```
These commands are enough to start using the program. For more detailed information and a description of advanced features, see the command descriptions.

## Commands
This is a list of all commands available in the program. Some commands can be run by typing just the first letter of the name.

### help
The help command displays a list of all commands available in the program and a brief description of each command's function and the arguments required (if any).

alternate name: h

### quit
Quit the program.

Alternate names: q, exit

### load
Create an automaton from a transition graph file or a regex. The command requires additional arguments as follows:
```
load [file] <FILENAME>
load -f <FILENAME>
load regex <REGEX>
load -r <REGEX>
```

When loading a file, if there are no lambda transitions and exactly one transition is defined for each state for each letter of the input alphabet,
the automaton is loaded as a DFA, otherwise it will be an NFA. All automata loaded from regexes are NFAs.

## File Format
Transition graphs can be specified in a plain text file. Lines beginning '#' are comments and will ignored.

A transition graph consists of state labels and transition lists.
The definition of a state consists of a state label, followed by optional initial and final state descriptors, and a list of transitions.
A state label has the form:
```
@mylabel
```
Note that '@' is not considered to be part of the label.
The symbol '!' indicates the initial state and '*' denotes a final state. A transition graph must have an initial state,
and it can have any number of final states. These symbols must appear at the start of a line.
A transition list has the form:
```
c state1 state2 ...
```
Here, c is the symbol consumed and state1, state2 ... are the labels of the states that are reached on that transition. 
A colon after the character is allowed, but not required. State labels can be separated by whitespace,
but other delimiters will be read as part of the state label.

Here is an example of a complete state description:
```
# My demo FSA diagram
@q0
!
b: q1 q2
a: q0
```
This represents an initial state called q0 that transitions to q1 and q2 on b and transitions to q0 (itself) on a.
## Regex Format
The program recognizes two kinds of regular expressions: primitive and derived. Any regex constructed according to these rules is valid.
In expressions containing both union and concatenation, concatenation is considered to have higher evaluation precedence.
* Primitive regexes:
  * ^ (matches the empty string)
  * ~ (null regex: matches nothing)
  * a-z (matches one alphabetic character)
* Derived regexes:
  * r* (star closure of regex r)   
  * rs (concatenation of regexes r and s)
  * r|s (union of regex r and s)
  * (r) where r is a regex

