from typing import Literal, TypeVar, Generic, Any, TypeGuard, Type
from abc import ABCMeta
from enum import Enum, auto

def isoncircuitpython() -> bool: ...
def enum_compat(cls):
    # --- DO NOT REMOVE THIS RETURN ---
    # pyright depends on this return to infer the type of the enum
    return cls

def warn(msg: str) -> None: ...

_T = TypeVar("_T")

class GenericABC(Generic[_T], metaclass=ABCMeta):
    pass

class MissingType(Enum):
    missing = auto()

Missing = MissingType.missing

def generic_compat(cls: Type[_T]) -> Type[_T]:
    """
    decorates to make a class in inheritable as a genric superclass
    @warning: on circuitpython, this wraps the class in an object to permit the [] syntax
    """
    # --- DO NOT REMOVE THIS RETURN ---
    # pyright depends on this return to infer the type of the enum
    return cls

class IsinstanceBase(type):
    def __instancecheck__(self, __instance: Any) -> TypeGuard[UID]: ...
