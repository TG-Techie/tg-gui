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

from typing import *

from .liststate import ListState, ListStateIterator, _LSIterMode

from tg_gui_platform.label import Label
from tg_gui_core import Widget

T = TypeVar("T")


def foe_VList__new__(
    gen: Generator[Widget, None, None]
) -> tuple[ListState[T], Callable[[T], Widget]]:
    # this assumes that the type dispatch for the different types of __new__ inputs is already handled

    assert (length := len(ListStateIterator._sugar_stack)) == 1, length  # type: ignore

    liststate, factory = ListState[T]._get_from_generator_(gen)

    assert (length := len(ListStateIterator._sugar_stack)) == 0, length  # type: ignore

    return (liststate, factory)


# example in context
def test_factory():
    # - start pretending this is a class body
    entries = ListState([1, 2, 3])

    ls, factory = foe_VList__new__(Label(str(i)) for i in entries)
    # - stop pretending this is a class body

    # ls and factory would be used inside the foe__new__ method, ie inside the VList Class

    # start asserts
    assert ls is entries, f"{ls=}, {entries=}"
    assert callable(factory)
    if not TYPE_CHECKING:
        assert isinstance(factory, ListStateIterator), factory

    lbl = factory(1)
    assert isinstance(lbl, Label)
    assert lbl.text == "1"


def test_iter():
    items = ListState([1, 2, 3])

    expected = (1, 2, 3)
    actual = tuple(items)

    assert expected == actual, f"{expected=} but got {actual=}"

    for index, (exp, act) in enumerate(zip(expected, items)):
        assert exp == act, f"items[{index}] != entries[{index}], {exp} != {act}"


def test():
    test_factory()
    test_iter()
    print("tests passed!")
