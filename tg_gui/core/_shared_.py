from __future__ import annotations

from random import randint

from ._implementation_support_ import isoncircuitpython

from typing import TYPE_CHECKING, TypeVar, Generic
from abc import ABC, abstractmethod

DescT = TypeVar("DescT")

if TYPE_CHECKING:
    from typing import Type

Pixels = int


UID = int

__next_int: UID = randint(0, 10)
del randint


def uid() -> UID:
    global __next_int
    new_uid = __next_int
    __next_int = UID(new_uid + 1)
    return new_uid
