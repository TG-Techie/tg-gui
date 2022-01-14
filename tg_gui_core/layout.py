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

from ._platform_support import isoncpython, isoncircuitpython, use_typing
from .base import uid, UID, Widget, _MISSING
from .container import Container, declarable
from .stateful import State

from .widget_builder import WidgetBuilder, _widget_builder_cls_format


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


if TYPE_CHECKING:
    # this function is a no-op for typing transparancy when using mypy but is overwritten below.
    # DO NOT add typing annotations or doc strings to this function.
    def layoutwidget(cls):
        cls

else:

    def layoutwidget(cls):
        """
        This decorator is used to pre-process layout class bodies.
        this looks for sugary widget builders (raw `my_builder = lambda: Widget(...)`, etc)
        and wraps them in WidgetBuilder objects.
        """
        assert isinstance(cls, type), f"@layoutwidget must decorator a class, got {cls}"
        assert issubclass(cls, Layout), f"@layoutwidget({cls}) does not subclass Layout"

        cls_layout = cls._layout_
        assert (
            cls_layout is not Layout._layout_
        ), f"subclasses of {Layout} must define a ._layout_(...) method, {cls} does not"

        if isinstance(cls_layout, FunctionType):
            cls._layout_ = cls_layout = LayoutMethod(cls._layout_)

        assert isinstance(
            cls_layout, LayoutMethod
        ), f"{cls}._layout_ must be a LayoutMethod, found {cls_layout}"

        _widget_builder_cls_format(cls)

        return cls


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


@declarable
class Layout(Container):
    def _build_(self, dim_spec):
        super(Container, self)._build_(dim_spec)
        self._screen_.on_container_build(self)  # platform tie-in

    def _layout_(self):
        raise NotImplementedError(
            f"{type(self)} does not implement the ._layout_(...) method"
        )

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


class _LayoutProxy(Generic[_L]):

    _not_present_sentinel = object()

    __slots__ = (
        "_id_",
        "_widget",
        "_selected",
        "_cache",
    )

    def __init__(self, proxied: _L) -> None:
        # TODO(TG-Techie): comment this! It works but it's not clear how/why things work
        self._id_: UID = uid()
        self._widget = proxied
        self._selected: Any | None = None
        self._cache: dict[str, Widget] = {}

    def __repr__(self) -> str:
        seldbg = "" if self._selected is None else f".{self._selected}"
        return f"<{type(self).__name__}: {self._id_} {self._widget}{seldbg}>"

    def __getattr__(self, name: str) -> Any:

        widget = self._widget
        cache = self._cache

        # TODO: add error and debug to this. use self._selected to track if the widget was layouted or not.

        if name not in cache:

            clsattr = getattr(type(widget), name, _MISSING)
            if not isinstance(clsattr, WidgetBuilder):
                return getattr(widget, name)

            else:
                built = clsattr.build(widget)
                return lambda pos, dim, *, __built=built, __wid=widget: (
                    print(pos, dim),
                    __wid._nest_(__built),
                    __built._build_(dim),
                    __built._place_(pos),
                    __built,
                )[-1]
        else:
            return cache[name]

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
