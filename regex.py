#! /usr/bin/python3

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
UNION_SYM = "+"
CAT_SYM = "."
STAR_SYM = "*"
OPERATOR_SYM = UNION_SYM, CAT_SYM, STAR_SYM

# Regex operators 
UNION = Operator(UNION_SYM, 1)
CAT = Operator(CAT_SYM, 2)
STAR = Operator(STAR_SYM, 3)

OPERATOR_DICT = {
    UNION_SYM: UNION,
    STAR_SYM: STAR,
    CAT_SYM: CAT,
    ")": None,
    None: None
}

class Regex_Node:
    pass

class Leaf_Node(Regex_Node):
    pass

class Character_Node(Leaf_Node):
    def __init__(self, char):
        self.char = char

    def __repr__(self):
        return self.char

class Lambda_Node(Leaf_Node):
    def __repr__(self):
        return LAMBDA_CHAR
    
class Null_Node(Leaf_Node):
    def __repr__(self):
        return NULL_CHAR
    
class Star_Node(Regex_Node):
    def __init__(self, child):
        self.child = self.simplify_child(child)

    def simplify_child(self, node):
        """remove redunant stars nodes from child of star node"""
        if isinstance(node, Star_Node):
            return node.child
        
        if isinstance(node, Union_Node):
            node.left = self.simplify_child(node.left)
            node.right = self.simplify_child(node.right)

        return node

    def __repr__(self):
        return f"({STAR_SYM} {repr(self.child)})"
    
class Bin_Op_Node(Regex_Node):
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        left = repr(self.left)
        if type(self) == type(self.left):
            left = left[3:-1]
        right = repr(self.right)
        if type(self) == type(self.right):
            right = right[3:-1]

        return f"({self.op.symbol} {left} {right})"
    
class Cat_Node(Bin_Op_Node):
    op = CAT

    def make(left, right):
        if isinstance(left, Lambda_Node):
            return right
        if isinstance(right, Lambda_Node):
            return left
        if isinstance(left, Null_Node):
            return left
        if isinstance(right, Null_Node):
            return right
        return Cat_Node(left, right)

class Union_Node(Bin_Op_Node):
    op = UNION

    def make(left, right):
        if isinstance(left, Null_Node):
            return right
        if isinstance(right, Null_Node):
            return left
        return Union_Node(left, right)


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

class Regex_Parser:
    def __init__(self, regex=None, buf=None):
        self.stack = Stack()
        if regex:
            self.buf = Char_Buffer(regex)
            self.inside_paren = False
        else:
            self.buf = buf
            self.inside_paren = True
    
    def push_character(self, c):
        if c == LAMBDA_CHAR:
            self.push_node(Lambda_Node())
        elif c == NULL_CHAR:
            self.push_node(Null_Node())
        else:
            self.push_node(Character_Node(c))
    
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
        next_char = self.buf.peek()
        prev_op = self.stack.top()
        next_op = OPERATOR_DICT.get(next_char, CAT)
        if prev_op and (not next_op or prev_op.priority >= next_op.priority):
            self.stack.pop()
            prev_node = self.stack.pop()
            if prev_op == CAT:
                self.push_node(Cat_Node.make(prev_node, node))
            elif prev_op == UNION:
                self.push_node(Union_Node.make(prev_node, node))
        else:
            self.stack.push(node)

    def push_implied_cat(self):
        """Insert cat operator between adjacent operands"""
        if isinstance(self.stack.top(), Regex_Node):
            self.stack.push(CAT)

    def get_result(self):
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
                self.push_character(c)

        # all characters read from buffer
        if self.inside_paren:
            raise SyntaxError("missing closing parenthesis")
        return self.get_result()

def parse(regex):
    return Regex_Parser(regex).parse()

if __name__ == "__main__":
    print(parse("(ab*+cd)*"))
    print(parse("ab*c+cd*e"))
