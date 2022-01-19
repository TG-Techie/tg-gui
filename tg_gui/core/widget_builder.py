from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Type, TypeVar, Generic, Callable, Any
from types import FunctionType

from .widget import Widget
from .superior_widget import SuperiorWidget
from .stateful import State

_SW = TypeVar("_SW", bound=SuperiorWidget)
_W = TypeVar("_W", bound=Widget)
_Fn = TypeVar("_Fn", bound=Callable)


class BuildError(Exception):
    pass


class WidgetBuilder(Generic[_SW, _W]):
    def __init__(self, fn: Callable[[_SW], _W]) -> None:
        # impl-test(assert (lambda:None).__name__ == "<lambda>")
        assert fn.__name__ == "<lambda>"
        self._fn = fn

    def __get__(self, owner: None | _SW, ownertype: Type[_SW]) -> Callable[[], _W]:
        return lambda *, __owner=owner, __widbuilder=self: __widbuilder.build(owner)  # type: ignore

    def build(self, owner: _SW) -> _W:
        proxy = _BuildProxy(owner)
        # this is explicitly the wrong type
        widget = self._fn(proxy)  # type: ignore[arg-type]
        proxy._close_build_()
        return widget


class _BuildProxy(Generic[_SW]):
    def __init__(self, proxied: _SW) -> None:
        self._proxied = proxied
        self._cache: dict[str, Any] = {}

    def __getattr__(self, name: str) -> Any:

        cache = self._cache
        if name in cache:
            return cache[name]

        proxied = self._proxied

        cls = type(proxied)
        clasattr = getattr(cls, name, None)
        if issubclass(clasattr, State):
            proxiedattr = clasattr
        elif isinstance(clasattr, FunctionType):
            proxiedattr = _ForwardMethodCall(
                bound=getattr(proxied, name),
                methodname=clasattr.__name__,
                clsname=f"{cls.__module__}.{cls.__qualname__}",
            )
        # tg-gui-featutre(experimental)
        elif hasattr(clasattr, "_build_proxy_"):
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


class _ForwardMethodCall(Generic[_Fn]):
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

        raise NotImplementedError

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
