#! /usr/bin/python3

# special regex characters
EMPTY_REGEX = "~"
LAMBDA_REGEX = "^"

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
    
# Operator symbols
UNION_SYM = "+"
CAT_SYM = "."
STAR_SYM = "*"
OPERATOR_SYM = UNION_SYM, CAT_SYM, STAR_SYM

# Regex operators 
UNION = Operator(UNION_SYM, 1)
CAT = Operator(CAT_SYM, 2)
STAR = Operator(STAR_SYM, 3)

class Character_Node:
    def __init__(self, char):
        self.char = char

    def __repr__(self):
        return self.char

class Star_Node:
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"({STAR_SYM} {repr(self.child)})"
    
class Bin_Op_Node:
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"({self.op.symbol} {repr(self.left)} {repr(self.right)})"
    
class Cat_Node(Bin_Op_Node):
    op = CAT

class Union_Node(Bin_Op_Node):
    op = UNION


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
        if op == CAT:
            node = Cat_Node(left, right)
        elif op == UNION:
            node = Union_Node(left, right)
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

    @staticmethod
    def simplify_star(node):
        """remove redunant stars nodes from child of star node"""
        if isinstance(node, Star_Node):
            return node.child
        
        if isinstance(node, Union_Node):
            node.left = Regex_Parser.simplify_star(node.left)
            node.right = Regex_Parser.simplify_star(node.right)

        return node

    def _operator(self, c, stack):
        """handle operator character"""
        if stack.empty() or isinstance(stack.top(), Operator):
            raise SyntaxError("missing operand")
        if c == UNION_SYM:
            stack.push(UNION)
        elif c == CAT_SYM:
            stack.push(CAT)
        else:
            # star operator
            stack_top = Regex_Parser.simplify_star(stack.pop())
            stack.push(Star_Node(stack_top))

    def _normal_char(self, c, stack):
        """handle character without special meaning"""
        stack.push_implied_cat()
        prev_op = None
        if not stack.empty():
            prev_op = stack.top()
        stack.push(Character_Node(c))

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
            if next_op is not None and prev_op.priority >= next_op.priority:
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
                    if stack.empty():
                        raise SyntaxError("empty parenthetical expression")
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
            if stack.empty():
                raise SyntaxError("empty string")
            stack.reduce_all()
            return stack.pop()
        raise SyntaxError("missing closing parenthesis")

def parse(regex):
    return Regex_Parser(regex).parse()

if __name__ == "__main__":
    print(parse("abc**"))
    print(parse("(a*+b*+c*+d*+e*)*"))

