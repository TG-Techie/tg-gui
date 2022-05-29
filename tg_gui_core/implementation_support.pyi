from typing import Literal, TypeVar, Generic, Any, TypeGuard, Type, Callable
from typing_extensions import Self
from abc import ABCMeta, abstractclassmethod
from enum import Enum, auto

__all__ = (
    "TYPE_CHECKING",
    "isoncircuitpython",
    "enum_compat",
    "Missing",
    "MissingType",
    "IsinstanceBase",
)

from typing import TYPE_CHECKING

def isoncircuitpython() -> bool: ...

_E = TypeVar("_E", bound=Enum)

def enum_compat(cls: Type[_E]) -> Type[_E]:
    return cls

def warn(msg: str) -> None: ...

_T = TypeVar("_T")

class MissingType(Enum):
    missing = auto()
    def __bool__(self) -> Literal[False]: ...

Missing = MissingType.missing

class _IsinstMeta(type):
    _inst_isinstance_check_: Callable[[object], TypeGuard[Self]]
    def __instancecheck__(self, __instance) -> bool: ...

class IsinstanceBase(metaclass=_IsinstMeta):
    @abstractclassmethod
    def _inst_isinstance_check_(self, __instance: Any) -> TypeGuard[Self]: ...
