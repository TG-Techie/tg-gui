# The MIT License (MIT)
#
# Copyright (c) 2021 Jonah Yolles-Murphy (TG-Techie)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys

# here for transparent typing when decorating enums
def enum_compat(cls):
    return cls


# --- platform optimization ---
if sys.implementation.name == "circuitpython":
    from . import _typing_bypass as _typing_bypass
    from . import _enum_bypass as _enum_bypass

    sys.modules["typing"] = _typing_bypass  # type: ignore
    sys.modules["enum"] = _enum_bypass  # type: ignore

    from supervisor import reload as guiexit

    use_typing = lambda: False
    isoncircuitpython = lambda: True
    enum_compat = _enum_bypass.enum_compat
elif sys.implementation.name == "cpython":
    from sys import exit as guiexit

    use_typing = lambda: True
    isoncircuitpython = lambda: False
    enum_compat = lambda cls: cls
else:
    raise Exception(
        f"unsupported python implementation: {sys.implementation.name}, "
        + "please open an issue at https://github.com/TG-Techie/tg-gui/issues/new?"
        + "title=unsupported%20python%20implementation%3A%20{sys.implementation.name}"
    )


# --- unique ids ---
UID = int

from random import randint  # type: ignore

_next_id = randint(0, 11)
del randint


def uid() -> UID:
    global _next_id
    id = _next_id
    _next_id += 1
    return id


# --- utils ---
def clamp(lower: int, value: int, upper: int) -> int:
    return min(max(lower, value), upper)
