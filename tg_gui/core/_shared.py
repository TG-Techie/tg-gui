from __future__ import annotations

from random import randint

from .implementation_support import isoncircuitpython

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


if TYPE_CHECKING or not isoncircuitpython():
    from enum import Enum, auto

    class _MissingType(Enum):
        missing = auto()

    _Missing = _MissingType.missing
else:
    _Missing = type("MissingType", (), {})() if __debug__ or TYPE_CHECKING else object()
