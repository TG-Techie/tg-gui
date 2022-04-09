from __future__ import annotations


from tg_gui.core import (
    widget,
    Widget,
    Pixels,
    BuildProxy,
    ContainerWidget,
    Theme,
    add_elemets,
)


from typing import TypeVar, ClassVar, Callable
from types import LambdaType
from abc import ABC, abstractmethod, abstractstaticmethod


from typing import TYPE_CHECKING, Generic, TypeVar, Callable

# annotation-only imports
if TYPE_CHECKING:
    from typing import Iterable
    from ._platform_.platform import Platform, NativeElement, NativeContainer

_W = TypeVar("_W", bound=Widget, covariant=True)
# _W = TypeVar("_W", bound=Widget, covariant=True)
# _V = TypeVar("_V", bound="View", contravariant=True)


@widget
class View(ContainerWidget, Generic[_W]):
    @abstractmethod
    def body(self) -> _W:
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        build_proxy = BuildProxy(self)
        cls = type(self)
        assert hasattr(cls, "body"), f"{cls} has no .body method"
        assert (
            isinstance(cls.body, LambdaType) and cls.body.__name__ == "<lambda>"
        ), f"{cls}.body is not a lambda, got {cls.body}"

        # assert (
        #     isinstance(cls.body, LambdaType)
        #     and cls.body.__name__ == "<lambda>"
        #     or isinstance(cls.body, WidgetBuilder)
        # ), f"{cls}.body is not a lambda or WidgetBuilder"

        self._body: _W = cls.body(build_proxy)
        build_proxy._close_build_()

    def _nested_widgets_(self) -> Iterable[Widget]:
        return (self._body,)

    def _on_nest_(self, superior: ContainerWidget, platform: Platform) -> None:
        self._body._nest_in_(self, platform)

    def _on_unnest_(self, superior: ContainerWidget, platform: Platform) -> None:
        assert (
            self._superior_ is not None
        ), f"{self} is not nested, internal error. This should not have been called"
        self._body._unnest_from_(self, self._platform_)

    @property
    def _native_(self) -> NativeContainer:
        return self._body._native_  # type: ignore[return-value]

    def _build_(self, suggestion: tuple[Pixels, Pixels]) -> None:
        body = self._body
        body._build_(suggestion)
        self._dims_ = body._dims_

    def _demolish_(self) -> None:
        self._body._demolish_()
        # pretend we're delteing the _dims_, but it's actuall using the placeholder from __init__
        self._dims_ = None  # type: ignore[assignment]

    def _place_(self, position: tuple[Pixels, Pixels]) -> None:
        body = self._body

        self._pos_ = (0, 0)
        self._abs_pos_ = add_elemets(self._superior_._abs_pos_, self._pos_)

        self._body._place_(position)

    def _pickup_(self) -> None:
        body = self._body
        body._pickup_()
        self._pos_ = None  # type: ignore[assignment]
        self._abs_pos_ = None  # type: ignore[assignment]

    def _show_(self) -> None:
        self._body._show_()

    def _hide_(self) -> None:
        self._body._hide_()
