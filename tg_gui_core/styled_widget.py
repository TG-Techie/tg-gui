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

from .base import Widget
from ._platform_support import enum_compat, isoncircuitpython
from .stateful import State

# from .specifiers import specify, Specifier

# from .style import Style, DerivedStyle
from .theming import Theme, themedwidget

from enum import Enum, auto
from typing import TYPE_CHECKING
import sys

if TYPE_CHECKING:
    from typing import *

    from .theming import Theme

    Native = Any

# --- exposed objects and namespaces ---
@enum_compat
class align(Enum):
    leading = auto()
    center = auto()
    trailing = auto()


Color = int


class color(Color):
    # TODO: consider make ready only using proerties and lambdas vs performance
    red: Color = 0xFF0000
    orange: Color = 0xFFA500
    yellow: Color = 0xFFFF00
    green: Color = 0x00FF00
    lightgreen: Color = 0xA0FFA0
    blue: Color = 0x0000FF
    purple: Color = 0xCC8899

    white: Color = 0xFFFFFF
    lightgray: Color = 0xC4C4C4
    gray: Color = 0x909090
    darkgray: Color = 0x606060
    black: Color = 0x000000

    # TODO: make these states
    system_fill: Color | State[Color] = 0x909090
    system_foreground: Color | State[Color] = 0xFFFFFF
    system_active_fill: Color | State[Color] = 0x505050
    system_active_foreground: Color | State[Color] = 0xFFFFFF
    system_background: Color | State[Color] = 0x000000

    def fromfloats(r, g, b):
        r = round(255 * r ** 1.125)
        g = round(255 * g ** 1.125)
        b = round(255 * b ** 1.125)
        return (r << 16) | (g << 8) | (b << 0)


# --- THE style widget base ---

Widget._offer_priority_ = 0
Widget._reserve_space_ = True
Widget._self_sizing_ = False


@themedwidget
class StyledWidget(Widget):

    # --- themeing ---
    # these are injected by @themedwidget
    _build_attrs_: ClassVar[set[str]] = set()
    _style_attrs_: ClassVar[set[str]] = set()

    # --- layout ---
    # these are defined in subclasses of StyledWidget, they can be
    _use_sug_width_: bool
    _use_sug_height_: bool

    # --- impl tie-in defined in subclass ---
    _impl_build_: ClassVar[Callable[...]]  # type: ignore
    _impl_set_size_: ClassVar[Callable]  # type: ignore
    _impl_apply_style_: ClassVar[Callable]  # type: ignore
    _impl_cache_: Any  # a standardized place to store extra info for implemnetation

    # --- themed attribure resoution linking ---
    # circuitpython does not have .mro() so @themedwidget() injects a link to the previous
    # TODO: see if .__bases__ can be used instead of this hack
    # TODO: this may be needed for later `_stylecls_mro_: tuple[Type[StyledWidget], ...] = ()`

    def __init__(
        self,
        # style=None,
        _margin_: int = None,
        **kwargs,
    ):

        # input validation
        given = set(kwargs)
        allowed = self._build_attrs_ | self._style_attrs_
        if len(extra := given - allowed):
            raise TypeError(f"{type(self).__name__} got unexpected style attrs {extra}")

        self._themed_attrs_ = kwargs

        self._impl_cache_ = None

        super().__init__(_margin_=_margin_)

    def _build_(self, dim_spec):

        # build the native widget
        attrs = {attr: getattr(self, attr) for attr in self._build_attrs_}
        native, suggested_size = self._impl_build_(**attrs)

        # validate the native element
        assert native is not None, f"{self} failed to build, (parent {self._superior_})"
        self._native_ = native

        # get the specfied height from the layout engine
        specd_wth, specd_ht = self._specify_dim_spec(dim_spec)
        sugd_wth, sud_ht = suggested_size

        # select between the specified and suggested height based styled widget's behavior
        wth = sugd_wth if self._use_sug_width_ and (sugd_wth is not None) else specd_wth
        ht = sud_ht if self._use_sug_height_ and (sud_ht is not None) else specd_ht

        super()._build_((wth, ht))

        self._impl_set_size_(native, self.width, self.height)

        # # --- register style states ---
        # TODO: handle state for styled widgets

        handler = self._apply_style
        themed_attrs = self._themed_attrs_
        for name, value in themed_attrs.items():
            # if isinstance(value, Specifier):
            #     value = themed_attrs[name] = specify(value, self)
            if isinstance(value, State) and name in self._style_attrs_:
                value._register_handler_(self, handler)
        else:
            handler()

    def _demolish_(self):
        stateful_attrs = self._themed_attrs_
        for name, state in self._themed_attrs_.values():
            if isinstance(state, State):
                state._deregister_handler_(self)

        return super()._demolish_()

    def _place_(self, pos_spec):
        if __debug__ and self.width > self._superior_.width:
            print(
                f"WARNING: {type(self).__name__}'s width {self.width} is greater than its "
                + f"parent {self._superior_}'s width {self._superior_.width}"
            )
        if __debug__ and self.height > self._superior_.height:
            print(
                f"WARNING: {type(self).__name__}'s height {self.height} is greater than its "
                + f"parent {self._superior_}'s height {self._superior_.height}"
            )
        return super()._place_(pos_spec)

    def _demolish_(self):
        if isinstance(self._stateful_attrs_, State):
            self._stateful_attrs_._deregister_handler_(self)
        super()._demolish_()

    def _apply_style(self, *_, **__) -> None:

        attrs = {name: getattr(self, name) for name in self._style_attrs_}
        attrs = {
            name: attr.value(self) if isinstance(attr, State) else attr
            for name, attr in attrs.items()
        }

        try:
            self._impl_apply_style_(self._native_, **attrs)
        except TypeError as err:
            fn = type(self)._impl_apply_style_
            msg = (
                f"WARNING: error while calling {self}._impl_apply_style_(...) "
                + f"from File {fn.__globals__['__name__'].replace('.', '/')}.py in {fn.__name__}"
            )
            if isoncircuitpython():
                print(msg)
                raise err
            else:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                frame = exc_tb.tb_frame
                msg += (
                    "\nprobably somewhere in"
                    + f"\n  File {repr(fn.__code__.co_filename)}, "
                    + f"line {fn.__code__.co_firstlineno}\n"
                    + "original exception in the `try:` statement near"
                    + f"\n  File {repr(frame.f_code.co_filename)}, line {frame.f_lineno}"
                )
                raise TypeError(msg) from err

    # def _apply_style_handler(self, style=None):

    #     attrs = {
    #         name: getattr(self, name)
    #         for name in self._all_style_attr_names_
    #         if self._allows_themed_stateful_attr_(name)
    #     }

    #     self._impl_apply_style_(self._native_, **attrs)


# def themedwidget(widcls: "Type['Widget']") -> "Type['Widget']":

#     assert issubclass(
#         widcls, StyledWidget
#     ), f"{widcls} does not subclass {StyledWidget}, cannot use @themedwidget on non-styled widget"

#     buildattrs = widcls._build_style_attrs_
#     statefulattrs = widcls._stateful_style_attrs_

#     assert buildattrs not in (
#         matched_build_conflict := cls
#         if (buildattrs is cls._build_style_attrs_)
#         else False
#         for cls in Theme._required_
#     ), (
#         f"{widcls} missing the ._build_style_attrs_ class attribute, "
#         + "@themedwidget classes require ._build_style_attrs_ attrs spec. "
#         + f"(ie found a dict that belongs to {matched_build_conflict})"
#     )

#     assert not any(
#         matched_stateful_conflict_dicts := (
#             cls if (statefulattrs is cls._stateful_style_attrs_) else False
#             for cls in Theme._required_
#         )
#     ), (
#         f"{widcls} missing the ._stateful_style_attrs_ class attribute, "
#         + "@themedwidget classes require ._stateful_style_attrs_  attrs spec. "
#         + f"(ie found a dict that belonges to {matched_stateful_conflict_dicts})"
#     )

#     assert (
#         len(
#             overlap := set(widcls._build_style_attrs_)
#             & set(widcls._stateful_style_attrs_)
#         )
#         == 0
#     ), f"overlapping build and stateful style attributes {overlap} in {widcls}"

#     for attr, allowed in buildattrs.items():
#         setattr(widcls, attr, ThemedAttribute(attr, False, widcls, allowed))

#     for attr, allowed in statefulattrs.items():
#         setattr(widcls, attr, ThemedAttribute(attr, True, widcls, allowed))

#     Theme._required_.add(widcls)

#     widcls._all_style_attr_names_ = {
#         attr
#         for attr in dir(widcls)
#         if isinstance(getattr(widcls, attr, None), ThemedAttribute)
#     }

#     return widcls

# setup base internal state
