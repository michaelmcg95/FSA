#! /usr/bin/python3

import string
from functools import reduce

# special regex characters
NULL_CHAR = "~"
LAMBDA_CHAR = "^"

class Char_Buffer:
    """Character buffer for reading characters one at a time from a string"""
    def __init__(self, s):
        self.buf = s
        self.i = 0
    
    def get_next(self):
        if self.empty():
            return None
        result = self.buf[self.i]
        self.i += 1
        return result
    
    def peek(self):
        if self.empty():
            return None
        return self.buf[self.i]    
    
    def empty(self):
        return self.i == len(self.buf)
    
class Operator:
    """Regex operator with precedence"""
    def __init__(self, symbol, priority):
        self.priority = priority
        self.symbol = symbol
    
    def __repr__(self):
        return self.symbol
    
# Operator symbols
UNION_SYM = "|"
CAT_SYM = "."
STAR_SYM = "*"
OPERATOR_SYM = UNION_SYM, CAT_SYM, STAR_SYM

# Regex operators 
UNION = Operator(UNION_SYM, 1)
CAT = Operator(CAT_SYM, 2)
STAR = Operator(STAR_SYM, 3)


class Regex_Node:
    def regex(self):
        pass

class Leaf_Node(Regex_Node):
    def regex(self):
        return self.char

class Character_Node(Leaf_Node):
    def __init__(self, char):
        self.char = char

    def __repr__(self):
        return self.char

class Lambda_Node(Leaf_Node):
    char = LAMBDA_CHAR

    def __repr__(self):
        return LAMBDA_CHAR
    
class Null_Node(Leaf_Node):
    char = NULL_CHAR

    def __repr__(self):
        return NULL_CHAR
    
class Star_Node(Regex_Node):
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"({STAR_SYM} {repr(self.child)})"
    
    def regex(self):
        if isinstance(self.child, Bin_Op_Node):
            return "({})".format(self.child.regex()) + STAR_SYM
        return self.child.regex() + STAR_SYM
    
class Bin_Op_Node(Regex_Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        left = repr(self.left)
        right = repr(self.right)

        # simplify nested operations of the same type -- e.g. (+ a b c)
        if type(self) == type(self.left):
            left = left[3:-1]
        if type(self) == type(self.right):
            right = right[3:-1]

        return f"({self.symbol} {left} {right})"
    
class Cat_Node(Bin_Op_Node):
    symbol = CAT_SYM

    def regex(self):
        left, right = self.left.regex(), self.right.regex()
        if isinstance(self.left, Union_Node):
            left = f"({left})"
        if isinstance(self.right, Union_Node):
            right = f"({right})"
        return left + right
        
class Union_Node(Bin_Op_Node):
    symbol = UNION_SYM

    def regex(self):
        return f"{self.left.regex()}{self.symbol}{self.right.regex()}"

CHAR_NODES = {c: Character_Node(c) for c in string.printable}
LAMBDA_NODE = Lambda_Node()
NULL_NODE = Null_Node()

def make_node(val):
    """Make a leaf node from value, if it is not already a node"""
    if isinstance(val, Regex_Node):
        return val
    if val == LAMBDA_CHAR:
        return LAMBDA_NODE
    if val == NULL_CHAR:
        return NULL_NODE
    return CHAR_NODES.get(val)

def union_all(regex_nodes):
    """Create the regex union of a list of nodes"""
    return reduce(Union_Node, regex_nodes, NULL_NODE)
        
class Stack():
    """Stack for holding operations and operands in regex string"""

    def __init__(self):
        self.stack = []

    def push(self, val):
        self.stack.append(val)

    def pop(self):
        return self.stack.pop()
    
    def top(self):
        if self.empty():
            return None
        return self.stack[-1]
    
    def size(self):
        return len(self.stack)
    
    def empty(self):
        return len(self.stack) == 0
    
    def __repr__(self):
        return repr(self.stack)

def simplify(node, desc_of_star=False):
    """Remove redundant nodes from regex parse tree"""

    # simplify star node
    if isinstance(node, Star_Node):
        # remove redunant star nodes from child of star node
        simplified_child = simplify(node.child, desc_of_star=True)
        if simplified_child in (LAMBDA_NODE, NULL_NODE):
            return LAMBDA_NODE
        if desc_of_star:
            return simplified_child
        node.child = simplified_child
        return node
    
    # binary op nodes
    if isinstance(node, Bin_Op_Node):
        desc_of_star = False if isinstance(node, Cat_Node) else desc_of_star
        node.left = simplify(node.left, desc_of_star)
        node.right = simplify(node.right, desc_of_star)

        #  simplify unions
        if isinstance(node, Union_Node):
            # remove null nodes
            if node.right == NULL_NODE:
                return node.left
            if node.left== NULL_NODE:
                return node.right
            
            # remove null nodes and duplicates
            if node.left == node.right:
                return node.left
            
            # remove lambda nodes in descendent of star node
            if desc_of_star:
                if node.left == LAMBDA_NODE:
                    return node.right
                if node.right == LAMBDA_NODE:
                    return node.left
        
        # simplify cat nodes with lambdas or nulls
        elif isinstance(node, Cat_Node):
            # remove concatenated lambda nodes
            if node.left == LAMBDA_NODE:
                return node.right
            if node.right == LAMBDA_NODE:
                return node.left

            # concatenation with null node yields a null node
            if node.right == NULL_NODE or node.left == NULL_NODE:
                return NULL_NODE
    return node

class Regex_Parser:
    def __init__(self, regex=None, buf=None):
        self.stack = Stack()
        if regex is not None:
            self.buf = Char_Buffer(regex)
            self.inside_paren = False
        else:
            self.buf = buf
            self.inside_paren = True
    
    def push_operator(self, c):
        """Push operator character"""
        if self.stack.empty() or isinstance(self.stack.top(), Operator):
            raise SyntaxError("missing operand")
        if c == UNION_SYM:
            self.stack.push(UNION)
        elif c == CAT_SYM:
            self.stack.push(CAT)
        else:
            # star operator
            self.push_node(Star_Node(self.stack.pop()))

    def push_node(self, node):
        """Push regex parse tree node"""
        self.push_implied_cat()

        # apply prev operation if higher priority than next operation
        prev_op = self.stack.top()
        next_op = self.get_next_op()
        if prev_op and (not next_op or prev_op.priority >= next_op.priority):
            self.stack.pop()
            prev_node = self.stack.pop()
            if prev_op == CAT:
                self.push_node(Cat_Node(prev_node, node))
            elif prev_op == UNION:
                self.push_node(Union_Node(prev_node, node))
        else:
            self.stack.push(node)

    def get_next_op(self):
        next_char = self.buf.peek()
        if next_char == ")" or next_char == None:
            return None
        if next_char == UNION_SYM:
            return UNION
        if next_char == STAR_SYM:
            return STAR
        return CAT

    def push_implied_cat(self):
        """Insert cat operator between adjacent operands"""
        if isinstance(self.stack.top(), Regex_Node):
            self.stack.push(CAT)

    def get_result(self):
        """Get result of finished evaluation"""
        if self.stack.empty():
            raise SyntaxError("empty expression")
        result = self.stack.pop()
        if isinstance(result, Operator) or not self.stack.empty():
            raise SyntaxError("malformed expression")
        return result
          
    def parse(self):
        """Create a parse tree from a regex string"""
        while not self.buf.empty():
            c = self.buf.get_next()
            if c == "(":
                self.push_implied_cat()
                self.push_node(Regex_Parser(buf=self.buf).parse())
            elif c == ")":
                if not self.inside_paren:
                    raise SyntaxError("unmatched parenthesis")
                else:
                    return self.get_result()
            elif c in OPERATOR_SYM:
                self.push_operator(c)
            else:
                self.push_node(make_node(c))

        # all characters read from buffer
        if self.inside_paren:
            raise SyntaxError("missing closing parenthesis")
        return self.get_result()

def parse(regex, simple=True):
    tree = Regex_Parser(regex).parse()
    if simple:
        tree = simplify(tree)
    return tree

if __name__ == "__main__":
    print(parse("((^|a)|(b|(c|^)(^|d)))***"))
    # print(parse("ab*|a(b|a)*b"))
