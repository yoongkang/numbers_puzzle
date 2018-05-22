import math
import operator
from itertools import permutations
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


def _get_groupings(nums):
    if len(nums) == 1:
        yield nums[0]
    elif len(nums) == 2:
        yield nums
    else:
        yield from (
            (xx, yy)
            for i in range(1, len(nums))
            for xx in _get_groupings(nums[:i])
            for yy in _get_groupings(nums[i:])
        )


def get_groupings(perms):
    for nums in perms:
        yield from _get_groupings(nums)


def _generate_candidates(nums):
    x, y = nums[0], nums[1]
    if not isinstance(x, tuple) and not isinstance(y, tuple):
        for name in OPERATIONS:
            yield (name, x, y)
    else:
        x_gens = [x] if not isinstance(x, tuple) else _generate_candidates(x)
        y_gens = [y] if not isinstance(y, tuple) else _generate_candidates(y)
        yield from (
            (name, a, b) for a in x_gens for b in y_gens for name in OPERATIONS
        )


def generate_candidates(numbers):
    all_permutations = (
        x for r in range(2, len(numbers) + 1) for x in permutations(numbers, r)
    )

    for g in get_groupings(all_permutations):
        yield from _generate_candidates(g)


@functools.lru_cache()
def compute(candidate):
    name, x, y = candidate
    child_x, child_y = x, y
    child_x = compute(x)[1] if isinstance(x, tuple) else x
    child_y = compute(y)[1] if isinstance(y, tuple) else y
    return candidate, OPERATIONS[name](child_x, child_y)


def get_best_candidates(candidates, final_result):
    best_candidate, best_result, exact_found = None, 0, False
    for candidate in candidates:
        try:
            n, r = compute(candidate)
        except (ValueError, ZeroDivisionError, TypeError, OverflowError):
            continue
        if abs(r - final_result) < abs(best_result - final_result):
            best_candidate, best_result = n, r
        if r == final_result:
            exact_found = True
            yield r, n
    if not exact_found:
        yield best_result, best_candidate


def parse(candidate, bracket=True):
    name, x, y = candidate
    symbol = SYMBOLS[name]
    child_x = parse(x) if isinstance(x, tuple) else str(x)
    child_y = parse(y) if isinstance(y, tuple) else str(y)
    result = f" {symbol} ".join([child_x, child_y])
    if bracket:
        return f"({result})"
    return result


# Example usage:
#
# if __name__ == "__main__":
#     input_numbers = (7, 2, 9, 7)
#     target = 211
#     for (x, y) in get_best_candidates(generate_candidates(input_numbers), target):
#         expr = parse(y, False)
#         print(f"{expr} = {x}")
