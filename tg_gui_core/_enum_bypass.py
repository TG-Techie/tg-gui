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

# --- easy conversion ---
#  run this then copy and paste the ConstantGroup(...) call into the ternimal
# >>> def ConstantGroup(a, s):
# ...     print(f"@enum_compat\nclass {a}(Enum):\n\t"+'\n\t'.join(f"{n} = auto()" for n in s))


class Enum:
    _compat_wrapped_ = False

    def __new__(cls, *_, **__):
        raise TypeError(
            f"Cannot make Enum '{cls.__name__}' instances on circuitpython, "
            + "decorate the class with @enum_compat"
        )

    def __init__(self, name: str, autoid: int):
        assert (
            self._compat_wrapped_
        ), f"{self.__class__.__name__} is not wrapped with @enum_compat"
        self._name: str = name
        # self._outer: type = outer
        self._vrnt_id = autoid

    def __eq__(self, other):
        return (
            self._vrnt_id == other._vrnt_id if isinstance(other, type(self)) else False
        )

    def __hash__(self):
        return hash(repr(self)) ^ hash(self._vrnt_id)

    def __repr__(self):
        return f"<{type(self).__name__}.{self._name}: {self._vrnt_id}>"


auto = lambda: None


def enum_compat(cls: type):

    assert issubclass(cls, Enum)
    cls._compat_wrapped_ = True

    cls.__new__ = lambda cls, *_: object.__new__(cls)  # type: ignore

    autoid = 0
    for name in dir(cls):
        attr = getattr(cls, name)

        if name.startswith("__") or callable(attr):
            continue

        if isinstance(attr, int):
            autoid = attr
        else:
            autoid += 1
        setattr(cls, name, cls(name, autoid))

    cls.__new__ = Enum.__new__  # type: ignore
    cls.__init__ = None  # type: ignore

    return cls
