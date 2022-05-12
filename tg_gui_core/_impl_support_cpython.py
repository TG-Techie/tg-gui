from __future__ import annotations

import sys

from typing import TYPE_CHECKING, TypeVar, Generic, Callable, TypeGuard, Literal

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
    Missing = None

    def __bool__(self) -> Literal[False]:
        return False

    def __repr__(self) -> str:
        return "Missing"

    @property
    def value(self) -> MissingType:
        return Missing


Missing = MissingType.Missing


def generic_compat(cls):
    return cls


class _IsinstMeta(type):
    check_if_isinstance: Callable[[object], TypeGuard[Self]]

    def _inst_isinstance_check_(self, __instance) -> bool:
        return self.check_if_isinstance(__instance)


class IsinstanceBase(metaclass=_IsinstMeta):
    pass


class GenericABC(Generic[_T], metaclass=ABCMeta):
    pass
