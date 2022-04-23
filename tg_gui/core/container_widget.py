from __future__ import annotations


from ._shared import Pixels
from .widget import Widget
from .themeing import Theme

from typing import TYPE_CHECKING, overload
from abc import ABC, abstractmethod, abstractproperty

# annotation-only imports
if TYPE_CHECKING:
    from typing import ClassVar, Iterable

    from .._platform_.platform import Platform, NativeContainer


class ContainerWidget(Widget, ABC):

    # enviroment: TODO: make this a thing later
    _theme_: Theme | None = None

    @abstractproperty
    def _native_(self) -> NativeContainer:
        raise NotImplementedError

    @_native_.setter
    def _native_(self, native: NativeContainer | None) -> None:
        """
        Do nothing if it is passed None
        """
        raise NotImplementedError

    @abstractmethod
    def _nested_widgets_(self) -> Iterable[Widget]:
        raise NotImplementedError

    def _on_nest_(self, platform: Platform) -> None:
        for widget in self._nested_widgets_():
            widget._nest_in_(self, platform)

    def _on_unnest_(self, platform: Platform) -> None:
        for widget in self._nested_widgets_():
            widget._unnest_from_(superior=self, platform=platform)

    # --- conveinience ---

    def _build_(self, suggestion: tuple[Pixels, Pixels]) -> None:
        """
        A convenience method to build the native container and deal with the native
        element linking. Call this after you have nested the tg-gui framework widgets
        and the self._dims_ attribute has been set.
        """
        platform = self._platform_
        self._native_ = native = platform.new_container(self._dims_)
        for widget in self._nested_widgets_():
            assert (
                widget._is_built()
            ), f"cannot build {self}, its subordinate widget {widget} is not built"
            platform.nest_element(native, widget._native_)

    def _demolish_(self) -> None:
        native = self._native_
        platform = self._platform_
        for widget in self._nested_widgets_():
            platform.unnest_element(native, widget._native_)
            widget._demolish_()
        else:
            self._dims_ = None  # type: ignore[assignment]

    # def _place_(self, position: tuple[Pixels, Pixels]) -> None:
    #     """
    #     A convenience method to place the native elements into their native containers.
    #     Call this after you have called _place_. This will set the postion of
    #     the underlying native elements
    #     """
    #     native = self._native_
    #     platform = self._platform_
    # for widget in self._nested_widgets_():
    #     platform.set_relative(native, widget._native_, position)

    def _pickup_(self) -> None:
        for widget in self._nested_widgets_():
            widget._pickup_()
        else:
            self._pos_ = None  # type: ignore[assignment]
            self._abs_pos_ = None  # type: ignore[assignment]

    def _show_(self) -> None:
        for widget in self._nested_widgets_():
            widget._show_()
        else:
            self._platform_.show_element(self._native_)

    def _hide_(self) -> None:
        self._platform_.hide_element(self._native_)
        for widget in self._nested_widgets_():
            widget._hide_()

    def _pprint(self, *, _indent: int = 0, format=repr) -> str:
        return format(self)
