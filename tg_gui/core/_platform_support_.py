from __future__ import annotations

from ._shared import uid, UID, Pixels, _Missing
from .widget import widget

from typing import TYPE_CHECKING, TypeVar
from types import ModuleType, FunctionType
from abc import ABC, abstractmethod

_Fn = TypeVar("_Fn", bound=FunctionType)

_MODULE_CACHE = "_platform_methods_"


class PlatformError(ImportError):
    pass


def _raise(e: Exception) -> None:
    raise e


# annotation only typing
if TYPE_CHECKING:
    from typing import Protocol

    class NativeElement(Protocol):
        pass

    NativeContainer = NativeElement


def platformmethod(fn: FunctionType) -> None:
    # put the fn into the list of platform methods in the module's globals

    assert isinstance(fn, FunctionType), f"{fn} is not a function, got {repr(fn)}"

    scope = fn.__globals__
    if _MODULE_CACHE not in scope:
        scope[_MODULE_CACHE] = {}

    cache: dict[str, FunctionType] = scope[_MODULE_CACHE]

    assert (
        fn.__name__ not in cache
    ), f"{scope['__name__']}.{fn.__name__} is already a platform method"

    cache[fn.__name__] = fn

    # when debugging, return a stubbed function that raises on exeption
    if __debug__:
        return lambda self, *_, __fnname=fn.__name__, **__: _raise(  # type: ignore
            RuntimeError(
                f"cannot call platformmethod in module, {self}.{__fnname}(...)"
            )
        )
    else:
        return None


if TYPE_CHECKING:

    def platformwidget(mod):
        return widget

else:

    def platformwidget(mod: ModuleType):
        """
        decorator for classes that require platform specific functions,
        pass it the platform module that contains the platform specific methods
        > :warning: this decorator is potentially designed to be pre-processed:
        > call it with `@platformwidget(_platform_.<module name>)`
        """
        return lambda cls: _platform_widget(cls, mod)


def _platform_widget(cls, mod: ModuleType):
    # put the class into the list of platform classes in the module's globals
    assert (
        cls._platform_module_name_ is None
    ), f"{cls} already has a platform module {cls._platform_module_name_}"

    if not hasattr(mod, _MODULE_CACHE):
        raise PlatformError(
            f"{mod.__name__} is not a platform module (or does not have any @platformmethod decorated functions)"
        )

    cache: dict[str, FunctionType] | None = getattr(mod, _MODULE_CACHE, None)
    if cache is None:
        raise PlatformError(
            f"{mod.__name__} already processed as a platform module, cannot be re-used"
        )

    # check target class does not already have methods of the same name
    clsbody = cls.__dict__
    assert 0 == len(
        overlap := set(clsbody) & set(cache)
    ), f"{cls.__name__} already has methods, cannot add platform methods: {overlap}"

    # patch the methods in
    for fnname, fn in cache.items():
        setattr(cls, fnname, fn)

    cls._platform_module_name_ = mod.__name__

    # mark the module as processed, ... and remove the cache
    setattr(mod, _MODULE_CACHE, None)

    return widget(cls)


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

    @abstractmethod
    def hidenative(
        self,
        element: NativeElement,
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    def shownative(self, element: NativeElement) -> None:
        raise NotImplementedError
