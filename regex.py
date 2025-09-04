#! /usr/bin/python3

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

    def __lt__(self, other):
        return self.priority < other.priority

# Operator symbols
UNION_SYM = "+"
CAT_SYM = "."
STAR_SYM = "*"
OPERATOR_SYM = UNION_SYM, CAT_SYM, STAR_SYM

# Regex operators 
UNION = Operator(UNION_SYM, 1)
CAT = Operator(CAT_SYM, 2)
STAR = Operator(STAR_SYM, 3)

class Regex_Node:
    def __init__(self, op):
        self.op = op
        self.children = []

    def add_child(self, child):
        self.children.append(child)

    def __repr__(self):
        result =  f"({self.op.symbol}"
        for child in self.children:
            if isinstance(child, str):
                result += f" {child}"
            else:
                result += f" {repr(child)}"
        result += ")"
        return result

class Stack():
    """Stack for holding operations and operands in regex string"""

    def __init__(self):
        self.stack = []

    def push(self, val):
        self.stack.append(val)

    def pop(self):
        return self.stack.pop()
    
    def top(self):
        return self.stack[-1]
    
    def size(self):
        return len(self.stack)
    
    def empty(self):
        return len(self.stack) == 0
    
    def reduce(self):
        """Apply the last operation in the stack and push back the result"""
        right = self.pop()
        op = self.pop()
        left = self.pop()
        node = Regex_Node(op)
        node.add_child(left)
        node.add_child(right)
        self.push(node)

    def reduce_all(self):
        """Reduce until stack contains a single value"""
        # check for operator missing operand
        if not self.empty() and isinstance(self.top(), Operator):
            raise SyntaxError("missing operand")
        
        while self.size() > 1:
            self.reduce()

    def push_implied_cat(self):
        """Insert concatenation operator if top of stack is not an operator"""
        if not self.empty() and not isinstance(self.top(), Operator):
            self.push(CAT)

class Regex_Parser:
    """Class for creating parse trees from regex expressions"""
    def __init__(self, regex):
        self.buf = Char_Buffer(regex)

    def _operator(self, c, stack):
        """handle operator character"""
        if stack.empty() or isinstance(stack.top(), Operator):
            raise SyntaxError("missing operand")
        if c == UNION_SYM:
            stack.push(UNION)
        elif c == CAT_SYM:
            stack.push(CAT)
        else:
            stack_top = stack.pop()
            node = Regex_Node(STAR)
            node.add_child(stack_top)
            stack.push(node)

    def _normal_char(self, c, stack):
        """handle character without special meaning"""
        stack.push_implied_cat()
        prev_op = None
        if not stack.empty():
            prev_op = stack.top()
        stack.push(c)

        # apply prev operation if higher priority than next operation
        if prev_op is not None and not self.buf.empty():
            next_char = self.buf.peek()
            next_op = None
            if next_char == STAR_SYM:
                next_op = STAR
            elif next_char == UNION_SYM:
                next_op = UNION
            elif next_char != ")":
                next_op = CAT
            if next_op is not None and prev_op > next_op:
                stack.reduce()
    
    def parse(self, recursive=False):
        """Create a parse tree from a regex string"""
        stack = Stack()
        while not self.buf.empty():
            c = self.buf.get_next()
            if c == "(":
                stack.push_implied_cat()
                stack.push(self.parse(recursive=True))
            elif c == ")":
                if recursive:
                    stack.reduce_all()
                    return stack.pop()
                raise SyntaxError("unmatched parenthesis")

            # operator character
            elif c in OPERATOR_SYM:
                self._operator(c, stack)

            # character without special meaning
            else:
                self._normal_char(c, stack)

        if not recursive:
            stack.reduce_all()
            return stack.pop()
        raise SyntaxError("missing closing parenthesis")

def parse(regex):
    return Regex_Parser(regex).parse()

print(parse("(a+b+c)"))

