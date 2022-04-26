from __future__ import annotations

from ._shared import uid, UID, Pixels

from .widget import Widget, widget
from .container_widget import ContainerWidget

# from .platform_support import _Platform_

from typing import TYPE_CHECKING, TypeVar, Generic, overload

try:

    import tg_debugtools as debug
    import builtins

    builtins.print = debug.new_printfn("{absfilepath}:{lineno}: {function}({self}):")

    del debug, builtins

    print("debug printing!!")
except:
    pass

if TYPE_CHECKING:
    from typing import Iterable, Literal

    from .._platform_.platform import Platform, NativeRootContainer

_W = TypeVar("_W", bound=Widget, covariant=True)


@widget
class RootWidget(ContainerWidget, Generic[_W]):
    """
    RootWidget is the top of the widget tree.
    It wraps a single child widget.
    It is the only widget that can be nested and does not have a superior.
    """

    _id_: UID

    _superior_: None  # type: ignore[assignment]
    _platform_: Platform

    _pos_: tuple[Pixels, Pixels] = None  # type: ignore[assignment]
    _abs_pos_: tuple[Pixels, Pixels] = None  # type: ignore[assignment]
    _dims_: tuple[Pixels, Pixels] = None  # type: ignore[assignment]
    _native_: NativeRootContainer = None  # type: ignore[assignment]

    # unique inst. attributes
    _wrapped: _W

    def __init__(
        self,
        widget: _W,
        *,
        platform: Platform,
        fit: bool = False,
        size: tuple[Pixels, Pixels] | None = None,
    ) -> None:
        self._id_ = uid()

        # None = fit size to the wrapped widget
        self._size_suggest = size or platform.default_size()
        self._fit = fit

        self._superior_ = None
        self._platform_ = platform

        self._pos_ = None  # type: ignore[assignment]
        self._abs_pos_ = None  # type: ignore[assignment]

        self._dims_ = None  # type: ignore[assignment]

        self._native_: NativeRootContainer | None = None

        self._wrapped: _W = widget
        widget._nest_in_(self, platform)

    def run(self) -> None:
        self._platform_.run()

    def setup(self) -> None:
        self._build_()
        self._place_(None)
        self._show_()

    def _nested_widgets_(self) -> Iterable[_W]:
        return (self._wrapped,)

    def _is_nested(self) -> bool:
        # TODO: review this... it's not tested but should never be...
        return True

    def _build_(self) -> None:

        suggest = self._size_suggest

        wrapped = self._wrapped

        wrapped._build_(suggest)
        self._dims_ = dims = wrapped._dims_ if self._fit else suggest

        print(dims)

        assert wrapped._native_ is not None, f"{wrapped} failed to build"
        platform = self._platform_

        # make the root element if it doesn't exist, or throw a fit if it does
        if platform.native_root is not None:
            raise RuntimeError(
                f"{platform} already has a root element, cannot build another root with size {self._size_suggest}. Found {platform.native_root}"
            )

        self._native_ = native = platform.init_native_root_container(dims)

        # nest the native element of that this widget wraps into the native root element
        platform.nest_element(native, wrapped._native_)

    def _demolish_(self) -> None:
        assert (
            self._native_ is not None
        ), "RootWidget._demolish_() called before _build_()"

        assert self._wrapped._native_ is not None, f"{self._wrapped} already demolished"
        self._platform_.unnest_element(self._native_, self._wrapped._native_)

        self._wrapped._demolish_()
        self._dims_ = None  # type: ignore[assignment]

        self._native_ = None

    def _place_(self, origin: tuple[Pixels, Pixels] | None) -> None:  # type: ignore[override]
        assert self._native_ is not None, "RootWidget._place_() called before _build_()"
        assert (
            self._wrapped._native_ is not None
        ), f"cannot please {self._wrapped}, it is not built"

        if origin is not None:
            raise NotImplementedError(
                f"RootWidget._place_() does not support origin {origin}, "
                + "possible future use still under consideration"
            )

        self._pos_ = (0, 0)
        self._abs_pos_ = (0, 0)

        wrapped = self._wrapped

        rt_w, rt_h = self._dims_
        wd_w, wd_h = wrapped._dims_
        pos = ((rt_w - wd_w) // 2, (rt_h - wd_h) // 2)
        wrapped._place_(pos)
        self._platform_.set_relative(self._native_, wrapped._native_, pos)

    def _pickup_(self) -> None:
        self._wrapped._pickup_()
        self._pos_ = None  # type: ignore[assignment]
        self._abs_pos_ = None  # type: ignore[assignment]

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
