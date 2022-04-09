from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Type, TypeVar, Generic, Callable, Any
from types import FunctionType

from .widget import Widget

# from .superior_widget import SuperiorWidget
from .stateful import State

# _SW = TypeVar("_SW", bound=SuperiorWidget)
_W = TypeVar("_W", bound=Widget)
_SW = TypeVar("_SW", bound=Widget)
_Fn = TypeVar("_Fn", bound=Callable)


class BuildError(Exception):
    pass


class WidgetBuilder(Generic[_SW, _W]):
    """
    A descriptor that can be used to build a widget with a given owner.
    wrap this around build lamdas to make them buildable, e.g.
    ```python
    @widget
    class MyWidget(...):
        body = WidgetBuilder(lambda self: ...)
    ```
    """

    def __init__(self, fn: Callable[[BuildProxy[_SW]], _W]) -> None:
        # impl-test(assert (lambda:None).__name__ == "<lambda>")
        assert fn.__name__ == "<lambda>"
        self._fn = fn

    def __get__(self, owner: None | _SW, ownertype: Type[_SW]) -> Callable[[], _W]:
        return lambda *, __owner=owner, __widbuilder=self: __widbuilder.build(owner)  # type: ignore

    def build(self, owner: _SW) -> _W:
        proxy = BuildProxy(owner)
        # this is explicitly the wrong type
        widget = self._fn(proxy)  # type: ignore[arg-type]
        proxy._close_build_()
        return widget


class BuildProxy(Generic[_SW]):
    def __init__(self, proxied: _SW) -> None:
        self._proxied = proxied
        self._cache: dict[str, Any] = {}

    def __getattr__(self, name: str) -> Any:

        cache = self._cache
        if name in cache:
            return cache[name]

        proxied = self._proxied

        cls = type(proxied)
        clsattr: Any = getattr(cls, name, None)
        proxiedattr: Any
        if isinstance(clsattr, State):
            proxiedattr = clsattr
        elif isinstance(clsattr, FunctionType):
            proxiedattr = ForwardMethodCall(
                bound=getattr(proxied, name),
                methodname=clsattr.__name__,
                clsname=f"{cls.__module__}.{cls.__qualname__}",
            )
        # tg-gui-feature(experimental): protocol for behavior in widget builder proxies
        elif hasattr(clsattr, "_build_proxy_"):
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


class ForwardMethodCall(Generic[_Fn]):
    def __init__(
        self,
        bound: _Fn,
        methodname: str,
        clsname: str,
    ) -> None:
        self._bound: _Fn | None = bound  # None is closed
        self._mthdname: str = methodname
        self._clsname: str = clsname
        self._calls: int = 0

    def __call__(self, *args: Any, **kwargs: Any) -> Callable[[], Any]:

        if self._bound is None:  # the builed has been closed
            raise RuntimeError(
                f"{type(self).__name__} called afer build closed, "
                + "methods must be called explicitly in widget builders. "
                + f"use `self.{self._mthdname}(...)` in `class {self._clsname}(...):`, "
                + f"(probably used only `self.{self._mthdname}`)"
            )
        elif len(args) == 0 and len(kwargs) == 0:
            self._calls += 1
            return self._bound
        else:
            self._calls += 1
            return lambda *, __args=args, __kwargs=kwargs, __bound=self._bound: __bound(  # type: ignore
                *__args, **__kwargs
            )

    def _close_build_(self) -> None:
        if self._calls == 0:
            raise BuildError(
                "methods must be called explicitly in widget builders. "
                + f"found `self.{self._mthdname}` in `class {self._clsname}(...):`, "
                + f"must call `self.{self._mthdname}(...)`"
            )
        self._bound = None
