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

from __future__ import annotations

from typing import TYPE_CHECKING
import builtins

if TYPE_CHECKING:
    from typing import *


class property:

    fget: Callable[[object], Any] | None
    fset: Callable[[object, object], None] | None

    def __init__(
        self,
        fget: Callable[[object], Any] | None = None,
        fset: Callable[[object, object], None] | None = None,
    ):
        self.fget = fget
        self.fset = fset

        if fget is not None and hasattr(fget, "__name__"):
            self._name = fget.__name__
        elif fset is not None and hasattr(fset, "__name__"):
            self._name = fset.__name__
        else:
            self._name = "<unnamed property>"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError(f"attribute .{self._name} is unreadbale")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError(f"can't set attribute .{self._name}")
        self.fset(obj, value)

    def getter(self, fget: Callable[[object], Any]) -> "property":
        return type(self)(fget, self.fset)

    def setter(self, fset: Callable[[object, object], None]) -> "property":
        return type(self)(self.fget, fset)

    # circuitpython compatiblity guard (for future features)
    __set_name__ = object()


orig_property = builtins.property
builtins.property = property
