from __future__ import annotations

import sys

from typing import TYPE_CHECKING, TypeVar, Generic, Callable, TypeGuard

if TYPE_CHECKING:
    from typing_extensions import Self


from abc import ABCMeta


def isoncircuitpython() -> bool:
    return False


enum_compat = lambda cls: cls


def warn(msg: str) -> None:
    raise Warning(msg)


_T = TypeVar("_T")


class GenericABC(Generic[_T], metaclass=ABCMeta):
    pass


from functools import wraps as _wraps

from enum import Enum, auto


class MissingType(Enum):
    missing = auto()


Missing = MissingType.missing


def generic_compat(cls):
    return cls


class _UIDMeta(type):
    __isinstance_hook__: Callable[[object], TypeGuard[Self]]

    def __instancecheck__(self, __instance) -> bool:
        return self.__isinstance_hook__(__instance)


class IsinstanceBase(metaclass=_UIDMeta):
    pass
