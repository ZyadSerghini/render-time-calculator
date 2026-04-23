"""
Test file to verify ruff and ty configuration.
Run: `ruff check test_linting.py` and `ty check test_linting.py`
Every line with an error is commented with the expected rule.
"""

# ============================================================
# RUFF ERRORS - Import related (I: isort)
# ============================================================
from typing import cast

# ============================================================
# RUFF ERRORS - Pyflakes (F)
# ============================================================

x = undefined_variable  # F821: undefined name


def unused_variable_func():
    unused = 42  # F841: local variable assigned but never used
    return 1


# ============================================================
# RUFF ERRORS - pycodestyle errors (E)
# ============================================================
y = 1  # E225: missing whitespace around operator
z = [1, 2, 3]  # E231: missing whitespace after ','

if True:
    pass
else:
    pass  # E111: indentation is not a multiple of 4


# ============================================================
# RUFF ERRORS - pycodestyle warnings (W)
# ============================================================
def trailing_whitespace():
    """Function with trailing whitespace above."""  # W291: trailing whitespace
    pass


# ============================================================
# RUFF ERRORS - flake8-bugbear (B)
# ============================================================
def mutable_default(items=[]):  # B006: mutable default argument
    items.append(1)
    return items


import unittest


class MyTest(unittest.TestCase):
    def test_example(self):
        with self.assertRaises(Exception):  # B017: assertRaises(Exception) too broad
            raise ValueError("error")


try:
    risky_operation = 1 / 0
except:  # B001: bare except
    pass


# ============================================================
# RUFF ERRORS - pyupgrade (UP)
# ============================================================
old_style_format = "Hello %s" % "world"  # UP031: use format specifiers instead of %

legacy_typing = "List[int]"  # This is a string, but let's show a real one:


def old_type_hints(items: list[int]) -> dict[str, int]:  # UP006: use list/dict instead
    return {}


# ============================================================
# TY ERRORS - Type checking
# ============================================================

# unresolved-reference (already covered by F821, but ty also catches it)
result = nonexistent_function()  # ty: unresolved-reference

# invalid-assignment
my_int: int = "this is a string"  # ty: invalid-assignment


# invalid-argument-type
def expects_int(value: int) -> int:
    return value * 2


expects_int("not an int")  # ty: invalid-argument-type

# call-non-callable
not_callable: int = 42
not_callable()  # ty: call-non-callable


# redundant-cast
def returns_str() -> str:
    return "hello"


redundant = cast(str, returns_str())  # ty: redundant-cast
