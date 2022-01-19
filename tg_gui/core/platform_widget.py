from __future__ import annotations

from .platform_support import requiredplatformmethod
from ._shared import uid, UID, Pixels
from .widget import Widget, widget
from .themeing import themedattr

from typing import TYPE_CHECKING, TypeVar, Generic
from abc import ABC, abstractmethod, abstractproperty


if TYPE_CHECKING:
    from typing import ClassVar

    from .platform_support import Platform, NativeElement, NativeContainer

_T = TypeVar("_T")

# --- platform widget ---
# TODO: Rename to PlatformWidget to something cooler (ie clearer and less boring)
@widget
class PlatformWidget(Widget):
    _native_: None | NativeElement = None

    # --- widget attributes ---
    _platform_module_name_: ClassVar[str | None] = None
    _margin_: Pixels = themedattr(default=5, init=False)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def _build_(self, suggestion: tuple[Pixels, Pixels]) -> None:
        assert self._is_nested()
        assert self._native_ is None
        w, h = suggestion
        self._native_, native_dims = self._build_native_(suggestion)

    def _demolish_(self) -> None:
        assert self._is_built()
        assert self._native_ is not None

    def _place_(self, position: tuple[Pixels, Pixels]) -> None:
        assert self._is_built()
        return super()._place_(position)

    def _pickup_(self) -> None:
        assert self._is_placed()
        return super()._pickup_()

    # --- platform methods ---
    # these are implemented in the platform-specific module
    @requiredplatformmethod
    def _build_native_(
        self,
        suggestion: tuple[Pixels, Pixels],
        **buildattrs,
    ) -> tuple[NativeElement, tuple[Pixels, Pixels]]:
        raise NotImplementedError

    @requiredplatformmethod
    def _native_style_(self, **styleattsr) -> None:
        raise NotImplementedError
