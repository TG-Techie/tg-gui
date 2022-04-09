from ._shared import uid, UID, Pixels, _Missing
from .widget import Widget, widget

from typing import (
    TYPE_CHECKING,
    TypeVar,
    ParamSpec,
    Generic,
    Callable,
    Concatenate,
    Type,
)
from types import (
    ModuleType as _ModuleType,
    FunctionType as _FunctionType,
    TracebackType as _TracebackType,
)
from abc import ABC, abstractmethod, abstractclassmethod, abstractproperty

class PlatformError(ImportError):
    pass

def platformwidget(mod: _ModuleType):
    return lambda cls: cls

def platformmethod(fn) -> None: ...

_P = ParamSpec(
    "_P"
)  # like [a, b, c] for Callable[[a, b, c], d] but just Callable[_P, d]
_R = TypeVar("_R")
_W = TypeVar("_W", bound=Widget)
# _RpmFn = TypeVar("_RpmFn", bound=Callable[_P, _R])

class requiredplatformmethod(Generic[_P, _R, _W]):
    def __init__(self, fn: Callable[Concatenate[_W, _P], _R]): ...
    def __get__(self, instance: _W, owner: type) -> Callable[_P, _R]: ...

class platformimports:
    def __enter__(self) -> None: ...
    def __exit__(
        self,
        exc_type: Type[BaseException],
        exc_value: BaseException,
        traceback: _TracebackType,
    ) -> None: ...
