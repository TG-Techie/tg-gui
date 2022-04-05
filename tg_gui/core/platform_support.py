from __future__ import annotations

from ._shared import uid, UID, Pixels, _Missing
from .widget import Widget, widget

from typing import TYPE_CHECKING, TypeVar
from types import ModuleType, FunctionType
from abc import ABC, abstractmethod, abstractclassmethod

# annotation only typing
if TYPE_CHECKING:
    from .platform_widget import PlatformWidget
    from .root_widget import RootWidget

    from typing import ClassVar, Callable, Type

    from .._platform_.platform import (
        NativeElement,
        NativeContainer,
        NativeRootContainer,
    )


_Fn = TypeVar("_Fn", bound=FunctionType)

_MODULE_CACHE = "_platform_methods_"


class PlatformError(ImportError):
    pass


def _raise(e: Exception) -> None:
    raise e


def platformwidget(mod: ModuleType):
    """
    decorator for classes that require platform specific functions,
    pass it the platform module that contains the platform specific methods
    > :warning: this decorator is potentially designed to be pre-processed:
    > only call it with `@platformwidget(_platform_.<module name>)`
    """
    if TYPE_CHECKING:
        return lambda cls: cls
    return lambda cls: _platform_widget(cls, mod)


def platformmethod(fn) -> None:
    """
    decorator for functions to make them as platform specific implementations of a method
    for a given widget. These are used in the _platform_ and related modules.
    > :warning: this decorator is potentially designed to be pre-processed:
    > only call it with `@platformwidget` or as otherwise documented
    """
    # put the fn into the list of platform methods in the module's globals

    assert isinstance(fn, FunctionType), f"{fn} is not a function, got {repr(fn)}"

    scope = fn.__globals__

    cache: dict[str, FunctionType] = scope.setdefault(_MODULE_CACHE, {})

    assert fn.__name__ not in cache, (
        f"{scope['__name__']}.{fn.__name__} is already a platform method, "
        + f"{cache[fn.__name__]}"
    )

    # add it to the listing of methods to be patched into the corresponding platform widgets
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


class requiredplatformmethod:
    """
    decorator for functions to make them as stubs that require a platform specific implementation
    (those are decorated with `@platformmethod`).
    """

    if __debug__:

        def __new__(cls, mthd: Callable) -> requiredplatformmethod:
            return _Missing  # type: ignore

        def __get__(self, _, cls: Type[PlatformWidget]):
            return lambda *_, **__: _raise(  # type: ignore
                PlatformError(
                    f"{cls} does not define a .{self._method_name}(...) platform method, "
                    + f"in the platform-specific module '{cls._platform_module_name_}'"
                    + (
                        f' "(probably in {cls._platform_module_name_.replace(".", "/")}.py)"'
                        if cls._platform_module_name_
                        else ""
                    )
                )
            )

    def __init__(self, mthd: Callable) -> None:
        self._method_name = mthd.__name__


class platformimports:
    """
    context manager used to mark the imports required for implementation specific methods
    wrap all imports excluding `__future__`, `TYPE_CHECKING`, and `_platform_support_` in this,
    EX:
    ```
    with platformimports():
        ...
    ```
    """

    _shared_inst: ClassVar[platformimports]

    def __enter__(self) -> None:
        pass

    def __exit__(self, *_, **__):
        return None

    # work-around for now, until (hopefully never) runtime import transplants are required
    def __new__(cls, *_, **__):
        if not hasattr(cls, "_shared_inst"):
            cls._shared_inst = super().__new__(cls)

        return cls._shared_inst


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
    if __debug__:
        for name, fn in cache.items():
            attr = getattr(cls, name, _Missing)
            if attr is _Missing or isinstance(attr, requiredplatformmethod):
                continue
            else:
                raise PlatformError(f"{cls} already has a .{name}(...) method, {attr}")

    # patch the methods in
    for fnname, fn in cache.items():
        setattr(cls, fnname, fn)

    cls._platform_module_name_ = mod.__name__

    # mark the module as processed, ... and remove the cache
    setattr(mod, _MODULE_CACHE, None)

    return widget(cls)


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
        """
        return the default platform for this class
        """
        raise NotImplementedError

    @abstractmethod
    def default_size(self) -> tuple[Pixels, Pixels]:
        """
        return the default size for this platform
        """
        raise NotImplementedError

    @abstractmethod
    def run(self, root: RootWidget) -> None:
        raise NotImplementedError

    @abstractmethod
    def new_container(self, dimensions: tuple[Pixels, Pixels]) -> NativeContainer:
        raise NotImplementedError

    @abstractmethod
    def new_root_container(
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
