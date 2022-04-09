from __future__ import annotations

from ._shared import uid, UID, Pixels

from .widget import Widget, widget
from .container_widget import ContainerWidget

# from .platform_support import _Platform_

from typing import TYPE_CHECKING, TypeVar, Generic

if TYPE_CHECKING:
    from typing import Iterable

    # from .platform_support import NativeRootContainer
    from .._platform_.platform import Platform, NativeRootContainer

_W = TypeVar("_W", bound=Widget, covariant=True)


@widget
class RootWidget(ContainerWidget, Generic[_W]):

    _id_: UID

    _superior_: None  # type: ignore[assignment]
    _platform_: Platform

    _pos_: tuple[Pixels, Pixels] | None = None
    _abs_pos_: tuple[Pixels, Pixels] | None = None

    _dims_: tuple[Pixels, Pixels] | None = None

    _native_: NativeRootContainer | None = None

    _wrapped: _W

    def __init__(
        self,
        widget: _W,
        *,
        platform: _Platform_,
    ):
        self._id_ = uid()

        self._superior_ = None
        self._platform_ = platform

        self._pos_ = None
        self._abs_pos_ = None

        self._dims_ = None

        self._native_: NativeRootContainer | None = None

        self._wrapped: _W = widget
        widget._nest_in_(self, platform)

    def setup(self, size: tuple[Pixels, Pixels] | None = None) -> None:
        size = size or self._platform_.default_size()
        self._build_(size)
        self._place_(None)

    def _nested_widgets_(self) -> Iterable[_W]:
        return (self._wrapped,)

    def _is_nested(self) -> bool:
        # TODO: review this... it's not tested but never will be...
        return True

    def _build_(self, exactly: tuple[Pixels, Pixels]) -> None:

        self._wrapped._build_(exactly)
        self._dims_ = exactly

        assert self._wrapped._native_ is not None, f"{self._wrapped} failed to build"
        platform = self._platform_
        self._native_ = native = platform.makeget_root_container(exactly)
        platform.nest_element(native, self._wrapped._native_)

    def _demolish_(self) -> None:
        assert (
            self._native_ is not None
        ), "RootWidget._demolish_() called before _build_()"

        assert self._wrapped._native_ is not None, f"{self._wrapped} already demolished"
        self._platform_.unnest_element(self._native_, self._wrapped._native_)

        self._wrapped._demolish_()
        self._dims_ = None

        self._native_ = None

    def _place_(self, origin: tuple[Pixels, Pixels]) -> None:  # type: ignore[override]
        assert self._native_ is not None, "RootWidget._place_() called before _build_()"
        assert (
            self._wrapped._native_ is not None
        ), f"cannot please {self._wrapped}, it is not built"

        self._pos_ = (0, 0)
        self._abs_pos_ = (0, 0)

        self._wrapped._place_((0, 0))
        self._platform_.set_relative(self._native_, self._wrapped._native_, (0, 0))

    def _pickup_(self) -> None:
        self._wrapped._pickup_()
        self._pos_ = None
        self._abs_pos_ = None

    def _show_(self) -> None:
        assert (
            self._wrapped._native_ is not None
        ), f"cannot show {self._wrapped}, it is not built"

        self._wrapped._show_()
        self._platform_.show_element(self._wrapped._native_)

    def _hide_(self) -> None:
        assert (
            self._wrapped._native_ is not None
        ), f"cannot hide {self._wrapped}, it is not built"

        self._platform_.hide_element(self._wrapped._native_)
        self._wrapped._hide_()
