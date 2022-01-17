from __future__ import annotations

from typing import *


def dec(cls):
    """
    add a doc string
    """
    if TYPE_CHECKING:
        return cls


@dec
class Foo:
    some_attr = 5


@dec
class Bar(Foo):
    other_attr = 6


Foo.s  # should suggest some_attr
Bar.s  # should suggest some_attr
Bar.o  # should suggest other_attr
