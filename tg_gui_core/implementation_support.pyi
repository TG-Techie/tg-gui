from typing import Literal, TypeVar, Generic, Any, TypeGuard, Type
from abc import ABCMeta
from enum import Enum, auto

def isoncircuitpython() -> bool: ...

_E = TypeVar("_E", bound=Enum)

def enum_compat(cls: Type[_E]) -> Type[_E]:
    return cls

def warn(msg: str) -> None: ...

_T = TypeVar("_T")

class GenericABC(Generic[_T], metaclass=ABCMeta):
    pass

class MissingType(Enum):
    missing = auto()
    def __bool__(self) -> Literal[False]: ...

Missing = MissingType.missing

def generic_compat(cls: Type[_T]) -> Type[_T]:
    """
    decorates to make a class in inheritable as a genric superclass
    @warning: on circuitpython, this wraps the class in an object to permit the [] syntax
    """
    ...

class IsinstanceBase(type):
    def __instancecheck__(self, __instance: Any) -> TypeGuard[UID]: ...
