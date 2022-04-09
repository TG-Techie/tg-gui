from ._shared import uid, UID, Pixels, _Missing
from .widget import Widget, widget

from .._platform_.platform import NativeElement, NativeContainer, NativeRootContainer

from typing import (
    TYPE_CHECKING,
    TypeVar,
    ParamSpec,
    Generic,
    Callable,
    Concatenate,
    Type,
    ClassVar,
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

# TODO: move this to a separate file
class _Platform_(ABC):
    """
    base class for platform support objects (thus the sunder name)
    """

    _id_: UID
    name: ClassVar[str]
    def __init__(self) -> None:
        self._id_ = uid()
    @abstractclassmethod
    def default(cls) -> _Platform_:

        raise NotImplementedError
    @abstractmethod
    def default_size(self) -> tuple[Pixels, Pixels]:

        raise NotImplementedError
    @abstractmethod
    def run(self) -> None:
        raise NotImplementedError
    @abstractmethod
    def new_container(self, dimensions: tuple[Pixels, Pixels]) -> NativeContainer:
        raise NotImplementedError
    @abstractproperty
    def native_root(self) -> NativeRootContainer | None:

        raise NotImplementedError
    @abstractmethod
    def init_native_root_container(
        self, dimensions: tuple[Pixels, Pixels]
    ) -> NativeRootContainer:

        raise NotImplementedError
    @abstractmethod
    def nest_element(
        self, container: NativeContainer, element: NativeElement
    ) -> NativeContainer:
        raise NotImplementedError
    @abstractmethod
    def unnest_element(
        self, container: NativeContainer, element: NativeElement
    ) -> None:
        raise NotImplementedError
    @abstractmethod
    def set_relative(
        self,
        container: NativeContainer,
        element: NativeElement,
        position: tuple[Pixels, Pixels],
    ) -> None:
        raise NotImplementedError
    @abstractmethod
    def hide_element(self, element: NativeElement) -> None:
        raise NotImplementedError
    @abstractmethod
    def show_element(self, element: NativeElement) -> None:
        raise NotImplementedError
