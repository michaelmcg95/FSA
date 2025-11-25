# Finite State Automata Simulator
By Michael McGuan

mcguanm@oregonstate.edu

For CS406 Fall 2025

Supervisor: Tim Alcon

## Table of Contents

[Summary](#summary)

[Requirements](#requirements)

[Getting Started](#getting-started)

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

[References](#references)

## Summary

This program simulates the operation of finite state automata. It supports both deterministic finite state automata (DFA) and nondeterministic finite state automata (NFA). The user will interact with the program via a command line interface.

To create an automaton the program will read a text file containing a description of the automaton's states and transitions. In addition to plain text format, the program supports importing Jflap xml files.

Alternatively, the user can input a regular expression (regex) and convert it to an equivalent NFA. 

Automata created from files are loaded as DFAs if they meet the requirements,
otherwise they are loaded as NFAs. All regexes are loaded as NFAs. Most functions are available to both types of automata, but certain functions are restricted to one type or the other.

Once an automaton is constructed, the user can test strings for acceptance. The program can read strings from the command prompt or read a batch of strings from a file. In trace mode, the program displays the sequence of states the automaton goes through as it processes the string.

The program allows the user to print a text description of the automaton's transition graph and save it to a file. Automata can also be exported to Jflap xml files.

Finally, the user can generate an equivalent regex from an automaton.

## Requirements
You must install Python to use this program. All functions have been tested with Python version 3.12.3.

## Getting Started
To start the program, navigate to the top level project directory and run the command
```
python3 UI.py
```
The first thing to do is to create an automaton. You can do this by loading one of the demo files.
```
> load demo
```
To see what this automaton does, you can print its transition diagram.
```
> print
if Label          Transitions
----------------------------------------------------------------------
!- q0              a: [q0], b: [q1]
-* q1
```
This output tells us that the automaton has two states labeled q0 and q1. The initial state is q0 and q1 is a final state.
From state q0, we can transition back to q0 on 'a' and to q1 on 'b'. This NFA corresponds to the regex a*b.

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
The last test '^' is a special character denoting the empty string.

To, generate the equivalent regex from this NFA, use the regex command.
```
> regex
a*b
```

You can also create an automaton from a regex like this:
```
load regex (aa|ab)*
```

These commands are enough to start using the program. For more detailed information and a description of advanced features, see the command descriptions.

## Commands
This is a list of all commands available in the program. As noted below, most commands can be run by typing just the first letter of the name. All commands and options are case insensitive. File names, regexes, and strings are case sensitive.

### help
The help command displays a list of all commands available in the program and a brief description of each command's function and the arguments required (if any).

Alternate name: h

### quit
Quit the program.

Alternate names: q, exit

### load
Create an automaton from a transition graph file or a regex. The command requires additional arguments as follows:
```
load [file | -f] <FILENAME>
load (regex | -r) <REGEX>
```
With the file or -f option, the command loads a transition file specified by FILENAME. If the file contains a syntax error, the load operation will be aborted and the program will display the error. Similarly, if the file is syntactically correct, but describes an invalid automaton, the load operation will fail. A transition graph is invalid if it has no initial state, multiple initial states, or a reference to an undefined state label.

With the regex or -r option, the command creates an automaton from the regex specified by REGEX.

When loading a file, if there are no lambda transitions and exactly one transition is defined for each state for each letter of the input alphabet,
the automaton is loaded as a DFA, otherwise it will be an NFA. All automata loaded from regexes are NFAs.

Alternate name: l

### test
Test if the current automaton accepts a string. This command can only be run if an automaton was already created. The syntax for running this command is:
```
load [backtrack | -b] <STRING>
```
The output will be "accept" if STRING is in the language of the automaton and "reject" otherwise.

If [tracing](#trace) is enabled, the program will print a history of the states the automaton enters as it processes the input. By default, the trace presents a nondeterministic view of NFAs and displays a list of concurrent states the NFA could be in for each character of the input consumed. If the backtrack option is given, the trace explores all paths through the transition graph and shows the NFA in a single state at a time. The backtrack option has no effect if tracing is disabled or the automaton is a DFA.

Alternate name: t

### batch
Test a collection of strings in a file.
```
batch <FILENAME>
```
The program opens the file specified by FILENAME and tests each line of the file with the current automaton. All leading and trailing whitespace is stripped from each line. If the line has only whitespace characters, it is interpreted as the empty string. The output will be the list of strings and their test results.

Example use:
```
> load -r (ab)*
regex loaded
> batch mystrings
^..............accept
ab.............accept
abab...........accept
ababab.........accept
b..............reject
a..............reject
ba.............reject
bbb............reject
```

Alternate name: b

### trace
Toggle tracing during tests. When enabled, the program displays additional information about the state history of the computation when running the [test](#test) command.

To demonstrate the two testing methods, consider the NFA defined in the file demo4.

```
> load demo4
file loaded
> p
if Label          Transitions
----------------------------------------------------------------------
!- 1              ^: [2], a: [7, 1, 5]
-- 2              ^: [3, 1]
-- 3              ^: [4]
-- 4              ^: [1, 2]
-- 5              b: [6]
-* 6              
-- 7              b: [8]
-- 8 
```

This is a sample trace using the concurrrent states test method (default): 

```    
> t ab
Remaining String    States
--------------------------------------------------------------------------------
ab                  {1, 4, 3, 2}
b                   {1, 4, 3, 5, 7, 2}
                    {6, 8}
accept
```

Here a trace of the same test using the backtracking method.

```
> t -b ab
Path                Remaining String    Message
--------------------------------------------------------------------------------
1                   ab                  entering state
1-2                 ab                  entering state
1-2-3               ab                  entering state
1-2-3-4             ab                  entering state
1-2-3-4-1           ab                  entering state
1-2-3-4-1           ab                  lambda cycle detected
1-2-3-4-2           ab                  entering state
1-2-3-4-2           ab                  lambda cycle detected
1-2-3-4             ab                  no path to final state
1-2-3               ab                  no path to final state
1-2-1               ab                  entering state
1-2-1               ab                  lambda cycle detected
1-2                 ab                  no path to final state
1-7                 b                   entering state
1-7-8                                   entering state
1-7-8                                   end of string but in nonfinal state
1-7                 b                   no path to final state
1-1                 b                   entering state
1-1-2               b                   entering state
1-1-2-3             b                   entering state
1-1-2-3-4           b                   entering state
1-1-2-3-4-1         b                   entering state
1-1-2-3-4-1         b                   lambda cycle detected
1-1-2-3-4-2         b                   entering state
1-1-2-3-4-2         b                   lambda cycle detected
1-1-2-3-4           b                   no path to final state
1-1-2-3             b                   no path to final state
1-1-2-1             b                   entering state
1-1-2-1             b                   lambda cycle detected
1-1-2               b                   no path to final state
1-1                 b                   no path to final state
1-5                 b                   entering state
1-5-6                                   entering state
1-5-6                                   end of string in final state
accept
```

### print
Display a text representation of the current automaton. The format of the display is the same as for [transition graph files](#file-format).

Alternate name: p

### write
Write the current automaton to a text file.
```
write <FILENAME>
```
The automaton is saved in [transition graph file format](#file-format).

Alternate name: w

### regex
Convert the current automaton to an equivalent regex. As demonstrated below, if the automaton was loaded from a regex, the output may not be precisely the same string as that used to create the automaton, but the regex will accept the same language.
```
> load -r a(b|c)
regex loaded
> regex
ab|ac
```

### import
Load an automaton from a Jflap xml file. This program was tested with Jflap version 7.1. This command will fail if the xml file cannot be parsed or the file describes an invalid automaton, as defined in the section on the [load](#load) command.

```
import <FILENAME>
```

Alternate name: i

### export
Save the current automaton in Jflap xml format. The file produced will be compatible with Jflap version 7.1. Note that the program makes no attempt to create an aesthetically pleasing transition diagram and simply places the states on a horizontal line.

```
export <FILENAME>
```

Alternate name: e

### reduce
Minimize the number of states in the current DFA. This command is only available for DFAs. The labels of the new states will be of the form {q0, q1, ...}, where q0, q1, ... are the labels of indistinguishable states in the old DFA.

Note: to convert an NFA to a DFA, use the command [dfa](#dfa).

### dfa
Convert the current NFA to a DFA. This command has no effect if the current automaton is already a DFA. The labels of the new states will be of the form {q0, q1, ...}, and the DFA will have a transition on character c from {s0, s1, ...} to {d0, d1, ...} if the NFA had a transition on c from any of the "s" states to any of the "d" states.

### type
Print the type (DFA or NFA) of the current automaton, or print a message that no automaton is loaded.

### label
Relabel the states of the current automaton. The labels will be created by enumerating the states in depth-first traversal order, starting with zero.

## File Format
Transition graphs can be specified in a plain text file. Lines beginning '#' are comments and will ignored.

A transition graph consists a list of state descriptions.
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

## References

Linz, Peter, and Susan H. Rodger. An Introduction to Formal Languages and Automata, Jones & Bartlett Learning, LLC, 2022. ProQuest Ebook Central, https://ebookcentral.proquest.com/lib/osu/detail.action?docID=6938285.

The methods for converting between NFAs and regexes, converting an NFA to a DFA, and constructing minimal DFAs were adapted from procedures described in chapters 2 and 3 of this book.

