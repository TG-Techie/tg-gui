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


class PassAll:
    def __init__(self, __name: str, ___getitem=[], **attrs: object) -> None:
        self.__name = __name

        assert isinstance(___getitem, list) and (
            len(___getitem) in {0, 1}
        ), f"expected an empty list or list containing one item, got {___getitem}"

        if len(___getitem) == 0:
            pass
        elif len(___getitem) == 1:
            self.__getitem = ___getitem[0]

        for attr, obj in attrs.items():
            setattr(self, attr, obj)

    def __getitem__(self, *args):
        if not hasattr(self, "__getitem"):
            raise TypeError(
                f"{repr(self)} does not support `{self.__name}[{','.join(repr(arg) for arg in args)}]`"
            )
        return self.__getitem

    def __repr__(self) -> str:
        return f"<Bypass '{self.__name}'>"


# patch in __future__ bypass
import builtins

builtins.Generic = PassAll("Generic", [object])  # type: ignore
builtins.TypeVar = lambda *_, **__: object  # type: ignore

sys.modules["__future__"] = PassAll("__future__", [], annotations=None)  # type: ignore


# --- platform optimization ---
if sys.implementation.name in ("circuitpython", "micropython"):
    isoncircuitpython = lambda: True

    # micropython does not have random.randint (:crying:)
    if sys.implementation.name == "micropython":
        randint = lambda *_: 0
    else:
        from random import randint  # type: ignore

    sys.modules["typing"] = PassAll("typing", [], TYPE_CHECKING=False)  # type: ignore

else:
    isoncircuitpython = lambda: False
    from typing import Type

    from random import randint  # type: ignore


# --- unique ids ---
UID = int

# start with a random base that is low
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


# --- enums... but not enums for now ---
# TODO: refactor into pigeon enums with sub-typing
class Constant:
    def __init__(self, outer, name):
        self._name = name
        self._outer = outer
        self._id = uid()

    def __eq__(self, other):
        return self._id == other._id if isinstance(other, type(self)) else False

    def __hash__(self):
        return hash(repr(self))

    def __repr__(self):
        return f"<Constant {self._outer._name}.{self._name}>"


# _ContGroupClassArgs: tuple[Type[type], ...] = (
#     () if usecircuitpythontyping() else (type,)
# )  # type: ignore


# class ConstantGroup(*_ContGroupClassArgs):  # type: ignore


class ConstantGroup:  # type: ignore
    def __init__(self, name, subs):
        self._name = name
        self._subs = subs_dict = {
            sub_name: Constant(self, sub_name) for sub_name in subs
        }
        # TODO: evaluate if this should stay removed to runtime memory...
        # # optimization for circuitpython to reduce function calls
        # for name, sub in subs_dict.items():
        #     setattr(self, name, sub)

    def __repr__(self):
        return f"<ConstantGroup {self._name}>"

    def __getattr__(self, name: str):
        if name in self._subs:
            return self._subs[name]
        else:
            return AttributeError(f"{self} has not attribute .{name}")
