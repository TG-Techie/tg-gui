# The MIT License (MIT)
#
# Copyright (c) 2021 Jonah Yolles-Murphy (TG-Techie)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import annotations

from ._implementation_support import isoncpython, isoncircuitpython, use_typing
from .base import uid, UID, Widget, _MISSING
from .container import Container
from .stateful import State

from .widget_builder import WidgetBuilder, Declarable


# from tg_gui_core.container import self as self_attrspec_cnstr
from typing import TYPE_CHECKING, TypeVar, Generic

_L = TypeVar("_L", bound="Layout")

if use_typing() or TYPE_CHECKING:
    from typing import Callable, Any, ClassVar, Type
    from types import FunctionType

    from .position_specifiers import PosSpec
    from .dimension_specifiers import DimSpec
else:

    @type
    def FunctionType():
        pass


_dot_prefix = ".{}".format


class LayoutError(RuntimeError):
    pass


class _LayoutProxy(Generic[_L]):

    _not_present_sentinel = object()

    __slots__ = (
        "_id_",
        "_proxied",
        "_selected",
        "_cache",
    )

    def __init__(self, proxied: _L) -> None:
        # TODO(TG-Techie): comment this! It works but it's not clear how/why things work
        self._id_: UID = uid()
        self._proxied = proxied
        self._selected: Any | None = None
        self._cache: dict[str, Widget] = {}

    def __repr__(self) -> str:
        seldbg = "" if self._selected is None else f".{self._selected}"
        return f"<{type(self).__name__}: {self._id_} {self._proxied}{seldbg}>"

    def __getattr__(self, name: str) -> Any:

        proxied = self._proxied
        selected = self._selected
        cache = self._cache

        # print(
        #     f"%> .{name}: ", self, proxied, selected, set(cache) if len(cache) else "{}"
        # )

        if selected is None and name in cache:
            # print("%> none selected, cache hit")
            return cache[name]
        elif selected is None:
            clsattr = getattr(type(proxied), name, _MISSING)
            # print(
            #     "%> none selected, cache miss",
            #     clsattr,
            #     isinstance(clsattr, WidgetBuilder),
            # )
            if isinstance(clsattr, WidgetBuilder):
                self._selected = selected = name
                return self
            else:
                attr = cache[name] = getattr((proxied), name)
                return attr
        elif selected == name:
            # print("%> selected, cache miss")
            raise LayoutError(
                f"error laying out {self._proxied}. "
                + f"`self.{selected}` is already selected, cannot select `self.{name}` again. "
                + f"ie call `self.{selected}(<pos>, <dims>)` before using `self.{name}` without calling it"
            )
        elif name in cache:
            # print(f"%> selected .{selected} but getting .{name} cache hit")
            return cache[name]
        elif selected != name:
            clsattr = getattr(type(proxied), name, _MISSING)
            if isinstance(clsattr, WidgetBuilder):
                raise LayoutError(
                    f"error laying out {self._widget}. "
                    + f"`self.{selected}` is already selected, cannot select "
                    + f"`self.{name}` before calling `self.{selected}(<pos>, <dims>)`. "
                )
            else:
                attr = cache[name] = getattr((proxied), name)
                return attr
        else:
            assert False, "unreachable"
            raise RuntimeError(f"unreachable?")

    def __call__(self, pos: PosSpec, dims: DimSpec) -> Widget:
        assert self._selected is not None, (
            f"error laying out {self._widget}. "
            + f"either the invalid syntax `self()` was used or "
            + f"`self.{self._selected}` was not selected before first. "
        )

        proxied = self._proxied
        selected = self._selected
        cache = self._cache

        assert selected not in cache, (
            f"error laying out {self._proxied}. "
            + f"`self.{selected})(...)` callbed but already in cache. as {cache[selected]}"
        )

        budiler = getattr(type(proxied), selected)
        assert isinstance(budiler, WidgetBuilder), (
            f"error laying out {self._proxied}. " + f"{budiler} is not a WidgetBuilder"
        )
        widget = budiler.build(proxied)
        proxied._nest_(widget)
        widget._build_(dims)
        widget._place_(pos)

        cache[selected] = widget
        self._selected = None

        return widget

    def close_layout(self):

        # circuitpython does not support __slots__ so we check for set attributes ater the fact
        if isoncircuitpython():
            assert 0 == len(
                extra_attrs := (set(self.__dict__) - set(self.__slots__))
            ), (
                "cannot set attributes inside of ._layout_ methods: "
                + f"{', '.join(map(_dot_prefix, extra_attrs))} set in {self._widget}._layout_(...)"
            )

    # add more explicit errors on full python implementations when setting attributes
    # inside of layout methods. (on circuitpython, this is not possible)
    if isoncpython() or TYPE_CHECKING:

        def __setattr__(self, name: str, value: Any) -> None:
            if name not in self.__slots__:
                raise AttributeError(  # !! this line is from tg-gui internals
                    f"cannot set attributes inside of ._layout_(...) methods, tried to assign to `{self._widget}.{name}`"
                )
            super().__setattr__(name, value)


class LayoutMethod:
    def __init__(self, fn: Callable[[Layout], None]):
        self._fn = fn

    def __get__(self, owner: Layout | None, owner_type: Type[Layout]):
        if owner is None:
            return self
        return lambda *, __owner=owner: self.layout(__owner)

    def layout(self, widget: Layout) -> None:
        proxy = _LayoutProxy(widget)
        self._fn(proxy)
        proxy.close_layout()
        del proxy


class Layout(Declarable):
    def _build_(self, dim_spec):
        super(Container, self)._build_(dim_spec)
        self._screen_.on_container_build(self)  # platform tie-in

    @classmethod
    def _layout_(cls):
        f"{cls} does not implement the ._layout_(...) method, subclasses of Layout must implement this method."

    def _build_(self, dim_spec) -> None:
        super(Container, self)._build_(dim_spec)
        self._screen_.on_container_build(self)

    def _place_(self, pos_spec):
        super(Container, self)._place_(pos_spec)
        self._layout_()

        self._screen_.on_container_place(self)

    def _show_(self):
        super(Container, self)._show_()
        for widget in self._nested_:
            widget._show_()

    @classmethod
    def _subclass_format_(cls, subcls) -> None:
        """
        This is called when Layout is subclassed subclasses
        """
        global __name__

        # skip formatting Layout
        if cls is subcls:
            return

        assert (
            subcls._layout_ is not Layout._layout_
        ), f"subclasses of {Layout} must define a ._layout_(...) method, {subcls} does not"

        if isinstance(subcls._layout_, FunctionType):
            subcls._layout_ = LayoutMethod(subcls._layout_)

        assert isinstance(
            subcls._layout_, LayoutMethod
        ), f"{subcls}._layout_ must be a LayoutMethod, found {subcls._layout_}"
