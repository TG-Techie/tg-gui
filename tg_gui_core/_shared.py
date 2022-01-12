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


def enum_compat(cls: type) -> type:
    return cls


# --- platform optimization ---
if sys.implementation.name in ("circuitpython", "micropython"):
    from supervisor import reload as guiexit

    def isoncircuitpython():
        return True

    USE_TYPING = False

    from . import typing_bypass as _typing_bypass
    from . import enum_bypass as _enum_bypass

    sys.modules["typing"] = _typing_bypass  # type: ignore
    sys.modules["enum"] = _enum_bypass  # type: ignore

    enum_compat = _enum_bypass.enum_compat
else:
    USE_TYPING = True
    from sys import exit as guiexit

    def isoncircuitpython():
        return False


# --- unique ids ---
UID = int

# start with a random base for id so they are not repeatable

# micropython does not have random.randint (:crying:)
if sys.implementation.name == "micropython":
    _next_id = int(0)
else:
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


import builtins
from builtins import print as _orig_print


if USE_TYPING or __debug__:
    if USE_TYPING:
        from typing import Callable, NoReturn

    def use_step_print_debugging(use_on: bool):
        if not use_on:
            builtins.print = _orig_print
        else:
            builtins.print = _step_print

    def _raise(exception):
        raise exception  # !! step print internals

    _step_cmds: dict[tuple[str, ...], tuple[Callable[[], None | NoReturn], str]] = {
        ("exit",): (guiexit, "exit the python instance"),
        ("raise",): (
            lambda: _raise(  # !! step print internals
                Exception("step print debug raise")
            ),
            "raise an exception",
        ),
        ("", "continue", "q"): (
            None,
            "exit the step session and conintue executing python as normal",
        ),
        ("help",): (
            lambda: _orig_print(
                "commands include:\n    "
                + "\n    ".join(
                    f"{', '.join(map(repr, cmd))}: \t{desc}"
                    for cmd, (_, desc) in _step_cmds.items()
                )
            ),
            "this help message",
        ),
    }

    def _step_print(*args, end: str = "\n", **kwargs):
        _orig_print(*args, **kwargs, end="")

        prompt_header = end.rstrip() + " "

        while True:
            cmd = input(prompt_header + "# (step cmd): ").strip()
            prompt_header = ""

            for cmds, (fn, _) in _step_cmds.items():
                if cmd in cmds:
                    if fn is not None:
                        fn()  # !! step print internals
                    else:
                        return
            else:
                print(f"Unkown command: `{cmd}`")
