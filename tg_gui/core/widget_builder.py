from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    ClassVar,
    Type,
    TypeVar,
    Generic,
    Callable,
    Any,
    Protocol,
)
from types import FunctionType

from .widget import Widget
from .stateful import State

# _SW = TypeVar("_SW", bound=SuperiorWidget)
_T = TypeVar("_T")
_W = TypeVar("_W", bound=Widget)
_SomeWidget = TypeVar("_SomeWidget", bound=Widget)
_Fn = TypeVar("_Fn", bound=Callable)

if TYPE_CHECKING:
    from typing import TypeGuard

    _BP = TypeVar("_BP", covariant=True)

    class BuildPoxyProvider(Protocol[_BP]):
        def _build_proxy_(self) -> _BP:
            ...

    _Bound = TypeVar("_Bound", covariant=True)
    _Owner = TypeVar("_Owner", contravariant=True)

    class Binding(Protocol[_Bound, _Owner]):
        def bound(self, *, relative_to: _Owner) -> _Bound:
            ...


def is_build_proxy_provider(obj: Any) -> TypeGuard[BuildPoxyProvider]:
    return hasattr(obj, "_build_proxy_") and callable(obj._build_proxy_)


def isbinding(obj: Any) -> TypeGuard[Binding]:
    return hasattr(obj, "bound") and callable(obj.bound)


class BuildError(Exception):
    pass


def _bind_if_bindable(binding: Binding, relative_to: Widget) -> Any:
    if isbinding(binding):
        return binding.bound(relative_to=relative_to)
    else:
        return binding


class WidgetBuilder(Generic[_SomeWidget, _W]):
    """
    A descriptor that can be used to build a widget with a given owner.
    wrap this around build lamdas to make them buildable, e.g.
    ```python
    @widget
    class MyWidget(...):
        body = WidgetBuilder(lambda self: ...)
    ```
    """

    def __init__(self, fn: Callable[[BuildProxy[_SomeWidget]], _W]) -> None:
        # impl-test(assert (lambda:None).__name__ == "<lambda>")
        assert fn.__name__ == "<lambda>"
        self._fn = fn

    def __get__(
        self, owner: None | _SomeWidget, ownertype: Type[_SomeWidget]
    ) -> Callable[[], _W]:
        return lambda *, __owner=owner, __widbuilder=self: __widbuilder.build(owner)  # type: ignore

    def build(self, owner: _SomeWidget) -> _W:
        proxy = BuildProxy(owner)
        # this is explicitly the wrong type
        widget = self._fn(proxy)  # type: ignore[arg-type]
        proxy._close_build_()
        return widget


class BuildProxy(Generic[_SomeWidget]):
    def __init__(self, proxied: _SomeWidget) -> None:
        self._proxied = proxied
        self._cache: dict[str, Any] = {}

    def __getattr__(self, name: str) -> Any:

        cache = self._cache
        if name in cache:
            return cache[name]

        proxied = self._proxied

        cls = type(proxied)
        cls_descriptor: Any = getattr(cls, name, None)
        proxiedattr: Any
        if isinstance(cls_descriptor, State):
            proxiedattr = cls_descriptor
        elif isinstance(cls_descriptor, FunctionType):
            proxiedattr = ForwardMethodCall(
                boundto=proxied,
                boundmethod=getattr(proxied, name),
                methodname=cls_descriptor.__name__,
                clsname=f"{cls.__module__}.{cls.__qualname__}",
            )
        # tg-gui-feature(experimental): protocol for behavior in widget builder proxies
        elif is_build_proxy_provider(cls_descriptor):
            # TODO: is this is implemented, add it to the State class
            return getattr(proxied, name)._build_proxy_()
        else:
            return getattr(proxied, name)

        cache[name] = proxiedattr
        return proxiedattr

    def _close_build_(self) -> None:
        for name, attr in self._cache.items():
            if hasattr(attr, "_close_build_"):
                attr._close_build_()

        self._cache = {}


class ForwardMethodCall(Generic[_SomeWidget, _Fn]):
    def __init__(
        self,
        boundto: _SomeWidget,
        boundmethod: _Fn,
        methodname: str,
        clsname: str,
    ) -> None:
        self._boundto: _SomeWidget | None = boundto
        self._boundfn: _Fn | None = boundmethod  # None is closed
        self._mthdname: str = methodname
        self._clsname: str = clsname
        self._calls: int = 0

    def __call__(self, *args: Any, **kwargs: Any) -> Callable[[], Any]:

        returnfn: Callable[[], Any]

        if self._boundfn is None or self._boundto is None:  # the builed has been closed
            raise RuntimeError(
                f"{type(self).__name__} called afer build closed, "
                + "methods must be called explicitly in widget builders. "
                + f"use `self.{self._mthdname}(...)` in `class {self._clsname}(...):`, "
                + f"(probably used only `self.{self._mthdname}`)"
            )

        elif len(args) == 0 and len(kwargs) == 0:
            self._calls += 1
            returnfn = self._boundfn
        # if any of the args and bindable, forward the call with the bound fn
        elif any(map(isbinding, args)) or any(map(isbinding, kwargs.values())):

            def bound_forward_method_proxy(
                *,
                __args=args,
                __kwargs=kwargs,
                __boundto=self._boundto,
                __boundfn=self._boundfn,
            ):
                args = (_bind_if_bindable(arg, __boundto) for arg in __args)
                kwargs = {
                    k: _bind_if_bindable(v, __boundto) for k, v in __kwargs.items()
                }
                __boundfn(*args, **kwargs)  # type: ignore

            returnfn = bound_forward_method_proxy
        else:

            def forward_method_proxy(
                *,
                __args=args,
                __kwargs=kwargs,
                __boundfn=self._boundfn,
            ):
                __boundfn(*__args, **__kwargs)  # type: ignore

            returnfn = forward_method_proxy

        self._calls += 1
        return returnfn

    def _close_build_(self) -> None:
        if self._calls == 0:
            raise BuildError(
                "methods must be called explicitly in widget builders. "
                + f"found `self.{self._mthdname}` in `class {self._clsname}(...):`, "
                + f"must call `self.{self._mthdname}(...)`"
            )
        self._boundto = None
        self._boundfn = None
