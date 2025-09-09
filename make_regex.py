#! /usr/bin/python3

from regex import *
import string

def _make_regex(num_var):
    if num_var == 1:
        return ["{}"]
    else:
        for num_left in range(1, num_var):
            left_exprs = _make_regex(num_left)
            right_exprs = _make_regex(num_var - num_left)
            result = []
            for l in left_exprs:
                for r in right_exprs:
                    if len(l) > 2:
                        l = f"({l})"
                    if len(r) > 2:
                        r = f"({r})"
                    for op in (CAT_SYM, UNION_SYM):
                        for lst in ("", STAR_SYM):
                            for rst in ("", STAR_SYM):
                                new_expr = f"{l}{lst}{op}{r}{rst}"
                                result.append(new_expr)
                                result.append(f"({new_expr}){STAR_SYM}")
        return result

def make_regex(num_var):
    letters = list(string.ascii_lowercase[:num_var])
    return [t.format(*letters) for t in _make_regex(num_var)]

if __name__ == "__main__":
    r = make_regex(2)
    for s in r:
        print("Regex: ", s)
        print("P:", "T:", "F:", sep="\n")


                                
