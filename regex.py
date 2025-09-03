#! /usr/bin/python3

import string

class Token:
    pass

class Char_Set(Token):
    def __init__(self, char_set):
        self.char_set = char_set
    def __repr__(self):
        return "".join(sorted(list(self.char_set)))

class Start_Group(Token):
    def __repr__(self):
        return "SG"

class End_Group(Token):
    def __repr__(self):
        return "EG"

class One_Plus(Token):
    def __repr__(self):
        return "1+"

class Zero_Plus(Token):
    def __repr__(self):
        return "0+"

class Zero_One(Token):
    def __repr__(self):
        return "0-1"

class Char_Literal(Token):
    def __init__(self, char):
        self.char = char

    def __repr__(self):
        return self.char

class CharBuffer:
    def __init__(self, s):
        self.buf = s
        self.put_back_chars = []
        self.i = 0
    
    def get_next(self):
        if self.put_back_chars != []:
            result = self.put_back_chars.pop()
        else:
            result =  self.buf[self.i]
            self.i += 1
        return result
    
    def put_back(self, c):
        self.put_back_chars.append(c)

    def empty(self):
        return self.i == len(self.buf) and len(self.put_back_chars) == 0

def read_char_set(buf):
    """Read character set descriptor"""
    cpl = False
    first = buf.get_next()
    if first == '^':
        cpl = True
    else:
        buf.put_back(first)
    chars = []
    at_end = False
    while not at_end:
        c = buf.get_next()
        if c == ']':
            at_end = True
        elif c == '\\':
            chars.append(buf.get_next())
        else:
            chars.append(c)
    return get_char_set(chars, cpl)
        
def complement(char_set):
    """Get complement of set of characters"""
    result = set(string.printable)
    for c in char_set:
        result.remove(c)
    return result

def get_char_set(char_list, cpl):
    """get set of characters specified by regex charset descriptor"""
    char_set = set()
    length = len(char_list)
    i = 0
    while i < length:
        if i < length - 2 and char_list[i + 1] == '-':
            first = ord(char_list[i])
            last = ord(char_list[i + 2])
            for char_code in range(first, last + 1):
                char_set.add(chr(char_code))
            i += 3
        else:
            char_set.add(char_list[i])
            i += 1
    if not cpl:
        return char_set
    return complement(char_set)

def tokenize(regex):
    tokens = []
    buf = CharBuffer(regex)
    while not buf.empty():
        c = buf.get_next()
        if c == '\\':
            tokens.append(Char_Literal(buf.get_next()))
        elif c == '[':
            tokens.append(Char_Set(read_char_set(buf)))
        elif c == '+':
            tokens.append(One_Plus())
        elif c == '*':
            tokens.append(Zero_Plus())        
        elif c == '?':
            tokens.append(Zero_One())
        elif c == '(':
            tokens.append(Start_Group())
        elif c == ')':
            tokens.append(End_Group())
        else:
            tokens.append(Char_Literal(c))
    return tokens

# print(sorted(list(read_char_set(CharBuffer("^abcdef\]g\\\\hij]")))))
# print(list(read_char_set(CharBuffer("\^abcdef\]g\\\\hij]"))))
# s = input("enter charset descriptor: ")
# print(read_char_set(CharBuffer(s)))

if __name__ == "__main__":
    print(tokenize("y(ab[45]*(3[m-o]?)+)+[1-2a-cq-r]?d*"))