from __future__ import annotations

from ._shared_ import uid, UID, Pixels

from typing import TYPE_CHECKING, TypeVar
from types import ModuleType, FunctionType
from abc import ABC, abstractmethod

_Fn = TypeVar("_Fn", bound=FunctionType)

# annotation only typing
if TYPE_CHECKING:
    from typing import *

    class NativeElement(Protocol):
        pass

    NativeContainer = NativeElement


def _raise(e: Exception) -> None:
    raise e


def requiredplatformmethod(fn: _Fn) -> _Fn:
    # TODO: maybe make this a class?
    raise NotImplementedError

    if __debug__:
        return lambda *_, **__: _raise(NotImplementedError(f"{fn} is not implemented"))
    else:
        return None


def platformmethod(fn) -> None:
    # put the fn into the list of platform methods in the module's globals

    raise NotImplementedError
    if __debug__:
        return lambda *_, **__: _raise(
            RuntimeError("cannot call platformmethod in module")
        )
    else:
        return None


def platformwidget(mod: ModuleType):
    """
    !!DO NOT ADD TYPE ANNOTATIONS TO THIS FUNCTION!!
    TODO: add docstring
    """
    if TYPE_CHECKING:
        return lambda cls: cls
    else:
        assert isinstance(cls, type) and issubclass(cls, PlatformWidget)

    raise NotImplementedError


# TODO: move this to a separate file
class Platform(ABC):
    _id_: UID

    def __init__(self) -> None:
        self._id_ = uid()

    @abstractmethod
    def newcontainer(self, width: Pixels, height: Pixels) -> NativeContainer:
        raise NotImplementedError

    @abstractmethod
    def nestelement(
        self, container: NativeContainer, element: NativeElement
    ) -> NativeContainer:
        raise NotImplementedError

    @abstractmethod
    def unnestelement(self, container: NativeContainer, element: NativeElement) -> None:
        raise NotImplementedError

    @abstractmethod
    def setrelative(
        self, container: NativeContainer, element: NativeElement, x: Pixels, y: Pixels
    ) -> None:
        raise NotImplementedError
