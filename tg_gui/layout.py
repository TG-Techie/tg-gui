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

_dot_prefix = ".{}".format


class BuildError(RuntimeError):
    pass


class LayoutError(RuntimeError):
    pass


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
        # TODO(TG-Techie): comment this! It works but it's not clear how/why things work
        self._container = layout
        self._selected: None | str = None
        self._inited_widgets: dict[str, Widget] = {}
        self._layedout_widgets: dict[str, Widget] = {}

    def __repr__(self) -> str:
        seldbg = "" if self._selected is None else f".{self._selected}"
        return f"<{type(self).__name__}: {self._id_} {self._container}{seldbg}>"

    def __getattr__(self, name: str) -> _LayoutProxy[_L] | Widget | State:

        # TODO: add error case (or support?) for a wiget builder referencing another widger builder
        # class Foo(Layout):
        #    body: WidgetBuilder = lamdba: HStack(self.foo)
        #    foo: WidgetBuilder = lambda: Lable("foo")

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
            if self._selected is None:
                self._inited_widgets[name] = self._init_new_widget(name, attr)
                self._selected = name
                return self
            else:
                raise LayoutError(
                    f"error in {self._container}._layout_(...) method. "
                    + f"tried to select self.{name} while {self._selected} is already selected (and not layed out). "
                    + f"be sure to call `self.{self._selected}(<pos>, <dims>)` before "
                    + f"laying out `self.{name}` or another widget"
                )

        elif in_layedout and not in_inited:
            return self._layedout_widgets[name]
        elif in_inited and not in_layedout:
            if self._selected is None:
                self._selected = name
                return self
            elif self._selected == name:
                raise LayoutError(
                    f"error in {self._container}._layout_(...) method. "
                    + f"`self.{name}` selected but not layed out. "
                    + f"`self.{name}` used before `self.{name}(<pos>, <dims>)` was called"
                )
            else:
                raise LayoutError(
                    f"error in {self._container}._layout_(...) method. "
                    + f"cannot select `self.{name}` while `self.{self._selected}` already selected. "
                    + f"be sure to call `self.{self._selected}(<pos>, <dims>)` before calling `self.{name}(...)`"
                )
        elif in_inited and in_layedout:
            # this may be pre-emptive but it's not a problem b/c there is a serious issue
            # if a user runs into this edge case. it shouldn't be possible but *shrug*
            raise LayoutError(
                f"error in {self._container}._layout_(...) method. "
                + f"some interal error occured while laying out `self.{name}`, both inited and layed out. "
                + f"please file an issue on github, "
                + "https://github.com/TG-Techie/tg_gui/issues/new?"
                + "title=Layout%20Error,%20widget%20during%20layout20is%20both%20inited%20and%20layedout"
                + "&body=Please%20describe%20the%20problem%20here."
            )
        else:
            assert False, "unreachable or internal error"

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
        ), f"{self._container}.{selected} has already been layed out, cannot be layed out again"
        assert (
            selected in self._inited_widgets
        ), f"internal error: {self._container}.{selected} has not been initialized. this is probably a bug in tg_gui_core"

        widget = self._inited_widgets.pop(selected)

        widget._build_(dim_spec)
        widget._place_(pos_spec)

        self._layedout_widgets[selected] = widget
        self._selected = None

        return widget

    def _init_new_widget(self, name: str, fn: Any) -> Widget:

        # otherwise, create a new widget and set it up
        if fn is None:
            raise AttributeError(f"{type(self._container)} has no attribute {name}")
        elif isoncircuitpython() and isinstance(fn, ClosureType):
            raise BuildError(
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
            raise BuildError(
                f"unkown binding of self for widget builder {type(self._container)}.{name}, expected no bound global for `self` or `tg_gui_core.container.self`. found {existing}"
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

    def _closing_asserts(self):
        assert len(self._inited_widgets) == 0, (
            (name := next(iter(self._inited_widgets))),
            (attrs := (", ".join(map(_dot_prefix, self._inited_widgets)))),
            f"{self._container}._layout_(...) finished with partially layed out widget(s): {attrs} . "
            + f"for example, `self.{name}` may have been use without "
            + f"`self.{name}(<pos>, <dims>)` being called first",
        )[-1]

        # circuitpython does not support __slots__ so we check for set attributes ater the fact
        if isoncircuitpython():
            assert 0 == len(
                extra_attrs := (set(self.__dict__) - set(self.__slots__))
            ), (
                "cannot set attributes inside of ._layout_ methods: "
                + f"{', '.join(map(_dot_prefix, extra_attrs))} set in {self._container}._layout_(...)"
            )

    # add more explicit errors on full python implementations when setting attributes
    # inside of layout methods. (on circuitpython, this is not possible)
    if not isoncircuitpython() or TYPE_CHECKING:

        def __setattr__(self, name: str, value: Any) -> None:
            if name not in self.__slots__:
                raise AttributeError(  # !! this line is from tg-gui internals
                    f"cannot set attributes inside of ._layout_(...) methods, tried to assign to `{self._container}.{name}`"
                )
            super().__setattr__(name, value)
