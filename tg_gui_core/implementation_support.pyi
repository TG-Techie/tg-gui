from typing import Literal, TypeVar, Generic, Any, TypeGuard, Type, Callable
from typing_extensions import Self
from abc import ABCMeta, abstractclassmethod
from enum import Enum, auto

def annotation_only() -> Literal[True]: ...
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

class _IsinstMeta(type, metaclass=ABCMeta):
    check_if_isinstance: Callable[[object], TypeGuard[Self]]
    def __instancecheck__(self, __instance) -> bool:
        return self.check_if_isinstance(__instance)

class IsinstanceBase(_IsinstMeta):
    @abstractclassmethod
    def _inst_isinstance_check_(self, __instance: Any) -> TypeGuard[Self]: ...
