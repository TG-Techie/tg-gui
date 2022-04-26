from __future__ import annotations

from .platform_support import requiredplatformmethod
from ._shared import uid, UID, Pixels
from .widget import Widget, widget, buildattr, BuildAttr
from .themeing import themedattr, ThemedAttr

from typing import TYPE_CHECKING, TypeVar, Generic
from abc import ABC, abstractmethod, abstractproperty


if TYPE_CHECKING:
    from typing import ClassVar

    from .container_widget import ContainerWidget
    from .._platform_.platform import Platform, NativeElement, NativeContainer

_T = TypeVar("_T")

# --- platform widget ---
# TODO: Rename to PlatformWidget to something cooler (ie clearer and less boring)
@widget
class PlatformWidget(Widget):
    _native_: None | NativeElement = None

    # --- widget attributes ---
    _platform_module_name_: ClassVar[str | None] = None
    _margin_: ThemedAttr[Pixels] = themedattr(default=30, build=True)

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def _on_nest_(self, platform: Platform) -> None:
        """
        Called when the widget is nested in a container widget. Not __TO__ nest this in a container widget,
        """
        pass

    def _on_unnest_(self, platform: Platform) -> None:
        pass

    def _build_(self, suggestion: tuple[Pixels, Pixels]) -> None:
        assert self._is_nested(), f"cannot build {self}, it is not nested"
        assert self._native_ is None
        w, h = suggestion
        self._native_, native_dims = self._build_native_(
            suggestion,
            **self._get_init_args(build=True),
        )
        self._dims_ = native_dims

    def _demolish_(self) -> None:
        assert self._is_built()
        assert self._native_ is not None

        self._native_ = None
        self._dims_ = None  # type: ignore[assignment]

    def _place_(self, position: tuple[Pixels, Pixels]) -> None:
        assert self._is_built(), f"cannot place {self}, it is not built"
        assert self._native_ is not None, f"cannot place {self}, it is not built"
        assert self._platform_ is not None, f"cannot place {self}, it is not nested"
        assert self._superior_ is not None, f"cannot place {self}, it is not nested"

        self._pos_ = w, h = position
        sw, sh = self._superior_._abs_pos_
        self._abs_pos_ = (sw + w, sh + h)
        self._platform_.set_relative(self._superior_._native_, self._native_, position)

    def _pickup_(self) -> None:
        assert self._is_placed(), f"cannot pickup {self}, it is not placed"
        return super()._pickup_()

    def _show_(self) -> None:
        assert self._platform_ is not None, f"cannot show {self}, it is not nested"
        assert self._native_ is not None, f"cannot show {self}, it is not built"

        self._platform_.show_element(self._native_)

    def _hide_(self) -> None:
        assert self._platform_ is not None, f"cannot show {self}, it is not nested"
        assert self._native_ is not None, f"cannot show {self}, it is not built"
        self._platform_.hide_element(self._native_)

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
