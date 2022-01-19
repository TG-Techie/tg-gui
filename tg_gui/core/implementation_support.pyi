from typing import Literal, TypeVar, Generic
from abc import ABCMeta

def isoncircuitpython() -> bool: ...
def class_id(cls: type) -> int: ...
def enum_compat(cls):
    # DO NOT REMOVE THIS RETURN
    return cls

def warn(msg: str) -> None: ...

_T = TypeVar("_T")

class GenericABC(Generic[_T], metaclass=ABCMeta):
    pass
