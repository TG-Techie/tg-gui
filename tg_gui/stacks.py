from __future__ import annotations

from tg_gui.core import (
    widget,
    Widget,
    Pixels,
    ContainerWidget,
    add_elemets as _add_elemets,
)
from ._platform_.platform import Platform, NativeContainer

from typing import TYPE_CHECKING, TypeVar, ClassVar, overload
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from typing import Iterable, SupportsIndex

    _Size = tuple[Pixels, Pixels]


class _XYStack(ContainerWidget, ABC):
    """
    A base class for stacks that place widget along an axis that fits to the space provided.
    """

    def __init__(self, *widgets: Widget, **kwargs):
        super().__init__(**kwargs)
        self._nested = widgets
        # pre-allocate space for the _native memeber
        self._native: NativeContainer = None  # type: ignore[assignment]

    def _fixed_axis_align(self, widget_fixed_dim: Pixels) -> Pixels:
        # TODO: implement alignment leding, trailing, center etc
        # if centered: return (self._split_size(self._dims_)[1] - fixed) // 2
        _, stack_fixed = self._split_size(self._dims_)
        # TODO: implement alignment leding, trailing
        # only center for now
        return (stack_fixed - widget_fixed_dim) // 2

    @abstractmethod
    def _split_size(self, size: _Size) -> _Size:
        """
        (width, height) -> (changing size, const_size)
        """
        raise NotImplementedError

    @abstractmethod
    def _merge_size(self, changing: Pixels, fixed: Pixels) -> _Size:
        """
        (changing size, const_size) -> (width, height)
        """
        raise NotImplementedError

    @property
    def _native_(self) -> NativeContainer:
        return self._native

    @_native_.setter
    def _native_(self, native: NativeContainer | None) -> None:
        if native is not None:
            self._native = native

    def _nested_widgets_(self) -> Iterable[Widget]:
        """
        Iterate over the widgets that are nested in this stack.
        """
        return iter(self._nested)

    def _build_(self, suggestion: _Size) -> None:
        # TODO: add build order
        nested = self._nested

        remaining, fixed = self._split_size(suggestion)

        n_widget = len(nested)

        self_change, self_fixed = 0, 0

        for widget in nested:
            dims = self._merge_size(round(remaining / n_widget), fixed)
            widget._build_(dims)
            c, f = self._split_size(widget._dims_)
            remaining = remaining - c
            self_change += c
            print(widget, (c, f), (self_change, self_fixed))
            self_fixed = max(self_fixed, f)
        else:
            self._dims_ = dims = self._merge_size(
                sum(self._split_size(w._dims_)[0] for w in nested),
                max(self._split_size(w._dims_)[1] for w in nested),
            )
        # finish native sterf
        super()._build_(dims)

    def _demolish_(self) -> None:
        self._demolish_()
        self._native = None  # type: ignore[assignment]

    def _place_(self, position: tuple[Pixels, Pixels]) -> None:
        self._pos_ = position
        self._abs_pos_ = _add_elemets(self._superior_._abs_pos_, position)

        running_pos = 0
        for widget in self._nested:
            subj_dim, fixed_dim = self._split_size(widget._dims_)

            pos = self._merge_size(running_pos, self._fixed_axis_align(fixed_dim))
            running_pos += subj_dim
            widget._place_(pos)


@widget
class VStack(_XYStack):
    def _split_size(self, size: _Size) -> _Size:
        w, h = size
        return h, w

    def _merge_size(self, changing: Pixels, fixed: Pixels) -> _Size:
        # put fixed back in width
        return fixed, changing


@widget
class HStack(_XYStack):
    def _split_size(self, size: _Size) -> _Size:
        return size

    def _merge_size(self, changing: Pixels, fixed: Pixels) -> _Size:
        return changing, fixed
