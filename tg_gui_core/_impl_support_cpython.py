from __future__ import annotations

import sys

from typing import TYPE_CHECKING, TypeVar, Generic, Callable, TypeGuard, Literal, Any

if TYPE_CHECKING:
    from typing_extensions import Self


from abc import ABCMeta, abstractclassmethod


def isoncircuitpython() -> bool:
    return False


enum_compat = lambda cls: cls


def warn(msg: str) -> None:
    raise Warning(msg)


_T = TypeVar("_T")


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


class _IsinstMeta(type):
    _inst_isinstance_check_: Callable[[object], TypeGuard[Self]]

    def __instancecheck__(self, __instance) -> TypeGuard[Self]:
        return self._inst_isinstance_check_(__instance)


class IsinstanceBase(metaclass=_IsinstMeta):
    @abstractclassmethod
    def _inst_isinstance_check_(self, __instance: Any) -> TypeGuard[Self]:
        ...


class GenericABC(Generic[_T], metaclass=ABCMeta):
    pass
