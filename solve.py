import math
import operator
from itertools import permutations, chain
import functools


MAX_POWER = 10
MAX_LSHIFT = 64
MAX_RSHIFT = 64


def hacked_pow(a, b):
    if b > MAX_POWER:
        raise ValueError("let's not use such high powers")
    return operator.pow(a, b)


def hacked_lshift(a, b):
    if b > MAX_LSHIFT:
        raise ValueError("let's not shift this much")
    return operator.lshift(a, b)


def hacked_rshift(a, b):
    if b > MAX_RSHIFT:
        raise ValueError("let's not shift this much")
    return operator.rshift(a, b)


OPERATIONS = {
    "add": operator.add,
    "mul": operator.mul,
    "sub": operator.sub,
    "div": operator.truediv,
    "floordiv": operator.floordiv,
    "lshift": hacked_lshift,
    "rshift": hacked_rshift,
    "mod": operator.mod,
    "pow": hacked_pow,
}

SYMBOLS = {
    "add": "+",
    "mul": "*",
    "sub": "-",
    "div": "/",
    "floordiv": "//",
    "lshift": "<<",
    "rshift": ">>",
    "mod": "%",
    "pow": "^",
}


def _generate(num, remaining):
    if len(remaining) == 1:
        for name in OPERATIONS:
            yield (name, num, remaining[0])
            yield (name, remaining[0], num)
    else:
        for name in OPERATIONS:
            for x in _generate(remaining[0], remaining[1:]):
                yield (name, num, x)
                yield (name, x, num)


def generate_formulas(numbers):
    all_permutations = (
        x for r in range(2, len(numbers) + 1) for x in permutations(numbers, r)
    )
    return chain(*(_generate(c[0], c[1:]) for c in all_permutations))


@functools.lru_cache()
def _compute(formula):
    name, x, y = formula
    child_x, child_y = x, y
    child_x = _compute(x)[1] if isinstance(x, tuple) else x
    child_y = _compute(y)[1] if isinstance(y, tuple) else y
    return formula, OPERATIONS[name](child_x, child_y)


def compute(formulas, final_result):
    best_formula, best_result, exact_found = None, 0, False
    for formula in formulas:
        try:
            n, r = _compute(formula)
        except (ValueError, ZeroDivisionError, TypeError, OverflowError):
            continue
        if abs(r - final_result) < abs(best_result - final_result):
            best_formula, best_result = n, r
        if r == final_result:
            exact_found = True
            yield r, n
    if not exact_found:
        yield best_result, best_formula


def parse(formula, bracket=True):
    name, x, y = formula
    symbol = SYMBOLS[name]
    child_x = parse(x) if isinstance(x, tuple) else str(x)
    child_y = parse(y) if isinstance(y, tuple) else str(y)
    formula = f" {symbol} ".join([child_x, child_y])
    if bracket:
        return f"({formula})"
    return formula


# Example usage:
#
# if __name__ == "__main__":
#     input_numbers = (75, 25, 50, 100, 8, 2)
#     target = 431
#     for (x, y) in compute(generate_formulas(input_numbers), target):
#         expr = parse(y, False)
#         print(f"{expr} = {x}")
