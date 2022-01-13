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


from tg_gui_core import (
    Widget,
    Container,
    declarable,
    State,
    isoncircuitpython,
    PositionSpecifier,
    DimensionSpecifier,
)
from tg_gui_core.container import self as self_attrspec_cnstr
from typing import TYPE_CHECKING, TypeVar, Generic

_L = TypeVar("_L", bound="Layout")

if TYPE_CHECKING or not isoncircuitpython():
    from types import FunctionType
    from typing import Callable, Any
else:

    @type
    def FunctionType():
        pass


if isoncircuitpython:
    ClosureType = type((lambda x: (lambda: x))(None))


@declarable
class Layout(Container):
    def _build_(self, dim_spec):
        super(Container, self)._build_(dim_spec)
        self._screen_.on_container_build(self)  # platform tie-in

    def _layout_(self):
        raise NotImplementedError(
            f"{type(self)} does not implement the ._layout_ method"
        )

    def _build_(self, dim_spec) -> None:
        super(Container, self)._build_(dim_spec)
        self._screen_.on_container_build(self)

    def _place_(self, pos_spec):
        super(Container, self)._place_(pos_spec)

        layout_fn = type(self)._layout_

        proxy = _LayoutProxy(self)
        # print(f"($) {type(self)}._layout_ is {layout_fn}")
        # print(f"($) calling with proxy = {proxy}")
        layout_fn(proxy)

        proxy._closing_asserts()
        self._screen_.on_container_place(self)

    def _show_(self):
        super(Container, self)._show_()
        for widget in self._nested_:
            widget._show_()

    # def _place_(self, pos_spec):
    #     super(Container, self)._place_(pos_spec)

    #     if hasattr(self, "_layout_"):
    #         self._layout_()
    #     elif hasattr(self, "_any_"):
    #         print(
    #             f"WARNING: ._any_(...) for layout will be depricated soon, use ._layout_(...) instead"
    #         )
    #         self._any_()
    #     else:
    #         raise RuntimeError(f"{self} has no ._layout_ method, define one")

    #     self._screen_.on_container_place(self)  # platform tie-in

    # def _layout_(self):
    #     raise NotImplementedError(
    #         f"layout methods must be written for subclasses of Layout"
    #     )


class _LayoutProxy(Generic[_L]):

    _not_present_sentinel = object()

    __slots__ = (
        "_container",
        "_selected",
        "_inited_widgets",
        "_layedout_widgets",
    )

    def __init__(self, layout: _L) -> None:
        self._container = layout
        self._selected: None | str = None
        self._inited_widgets: dict[str, Widget] = {}
        self._layedout_widgets: dict[str, Widget] = {}

    def __getattr__(self, name: str) -> _LayoutProxy[_l] | Widget | State:

        not_present = self._not_present_sentinel
        attr = getattr(type(self._container), name, not_present)

        if attr is not_present or isinstance(
            attr, (property, classmethod, staticmethod)
        ):
            return getattr(self._container, name)

        in_inited = name in self._inited_widgets
        in_layedout = name in self._layedout_widgets

        if isinstance(attr, State):
            return attr
        # if the widget has already been processed and layout out, return it
        elif not in_inited and not in_layedout:
            self._inited_widgets[name] = self._init_new_widget(name, attr)
            self._selected = name
            return self
        elif in_inited:
            self._selected = name
            return self
        elif in_layedout:
            return self._layedout_widgets[name]
        else:
            assert False, "unreachable"

    def __call__(
        self,
        pos_spec: (
            tuple[int | PositionSpecifier, int | PositionSpecifier] | PositionSpecifier
        ),
        dim_spec: (
            tuple[int | DimensionSpecifier, int | DimensionSpecifier]
            | DimensionSpecifier
        ),
    ) -> Widget:
        selected = self._selected
        assert (
            selected is not None
        ), f"no widget has been selected. use `self.<widget builder name>(pos, dims)` to select a widget to layout"
        assert (
            selected not in self._layedout_widgets
        ), f"{self._container}.{selected} has already been layedout, cannot be layedout again"
        assert (
            selected in self._inited_widgets
        ), f"internal error: {self._container}.{selected} has not been initialized. this is probably a bug in tg_gui_core"

        widget = self._inited_widgets.pop(selected)

        widget._build_(dim_spec)
        widget._place_(pos_spec)

        self._layedout_widgets[selected] = widget

        return widget

    def _closing_asserts(self):
        assert len(self._inited_widgets) == 0, (
            f"{self._container} has partially layedout widgets: "
            + f"{set(map('.{}'.format, self._inited_widgets))}"
            + "this could be caused by using "
        )

        # circuitpython does not support __slots__ so we check for set attributes ater the fact
        if isoncircuitpython():
            assert 0 == len(
                extra_attrs := (set(self.__dict__) - set(self.__slots__))
            ), (
                "cannot set attributes inside of ._layout_ methods: ",
                f"{set(map('.{}'.format, extra_attrs))} set in {self._container}._layout_(...)",
            )

    def _init_new_widget(self, name: str, fn: Any) -> Widget:

        # otherwise, create a new widget and set it up
        if fn is None:
            raise AttributeError(f"{type(self._container)} has no attribute {name}")
        elif isoncircuitpython() and isinstance(fn, ClosureType):
            raise RuntimeError(
                f"found a closure for {type(self._container)}.{name}. "
                + "This may be an error in writing a widget builder or a bug in tg_gui_core. "
                + "Please file and issue at https://github.com/TG-Techie/tg-gui/issues/new"
            )

        assert isinstance(
            fn, FunctionType
        ), f"{type(self._container)}.{name} unknown type for widget builder. expected a lambda, got {fn}"

        assert fn.__name__ == "<lambda>", (
            f"{type(self._container)}.{name} is not a lambda. "
            + f"use `{name} = lambda: <Widget(...)>` to declare widget builders"
        )

        fn: Callable[[], Widget] = fn

        return self._widget_from_builder(name, fn)

    def _widget_from_builder(self, name: str, fn: Callable[[], Widget]) -> Widget:
        # make sure the self attribute specifies constructor is injected into the global scope for the widget builder
        not_present = self._not_present_sentinel
        scope = fn.__globals__

        # get the current value in the scope
        existing = scope.get("self", not_present)
        # if something else is there, bail by raising an error
        if existing is not not_present and existing is not self_attrspec_cnstr:
            raise RuntimeError(
                f"unkown binding of self in {type(self._container)}.{name}, expected unbound or `tg_gui_core.container.self`. found {existing}"
            )

        # inject then build
        scope["self"] = self_attrspec_cnstr
        widget = fn()

        self._container._nest_(widget)

        # restore the original value
        if existing is not_present:
            scope.pop("self", None)
        else:
            scope["self"] = existing

        return widget
