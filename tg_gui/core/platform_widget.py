from __future__ import annotations

from ._implementation_support_ import isoncircuitpython
from ._shared import uid, UID, Pixels
from .widget import Widget, widget
from .themeing import themedattr

from typing import TYPE_CHECKING, TypeVar, Generic
from abc import ABC, abstractmethod, abstractproperty


if TYPE_CHECKING:
    from typing import Type, Any

    from ._platform_support_ import Platform, NativeElement, NativeContainer

_T = TypeVar("_T")

# --- platform widget ---
# TODO: Rename to PlatformWidget to something cooler (ie clearer and less boring)
@widget
class PlatformWidget(Widget):

    # --- widget attributes ---
    _platform_module_name_: str | None = None
    _margin_: Pixels = themedattr(default=5)  # type: ignore[assignment]

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
    def _build_native_(
        self,
        suggestion: tuple[Pixels, Pixels],
        **buildattrs,
    ) -> tuple[NativeElement, tuple[Pixels, Pixels]]:
        raise NotImplementedError

    def _native_style_(self, **styleattsr) -> None:
        raise NotImplementedError

    # --- check that platform methods were implemented ---
    @classmethod
    def _subclass_sugar_(cls, subcls: Type[PlatformWidget]) -> None:
        if cls is subcls:
            return

        assert subcls._build_native_ is not cls._build_native_, (
            f"{subcls} does not must define ._build_native_(...) method, it may not be defined "
            + f"in the platform-specific module '{subcls._platform_module_name_}'"
            + f' "(probably at {subcls._platform_module_name_.replace(".", "/")}.py)"'
        )
        assert subcls._native_style_ is not cls._native_style_, (
            f"{subcls} does not must define ._native_style_(...) method, it may not be defined "
            + f"in the platform-specific module '{subcls._platform_module_name_}'"
            + f' "(probably at {subcls._platform_module_name_.replace(".", "/")}.py)"'
        )
