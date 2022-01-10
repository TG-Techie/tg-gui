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

from .base import Widget, InheritedAttribute, LazyInheritedAttribute
from .specifiers import specify
from .stateful import State
from .style import Style, DerivedStyle
from .theming import (
    Theme,
    ThemedAttribute,
)

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import *

    from .theming import Theme

    Native = Any

    StyleSpec = ClassVar[dict[str, type | tuple[type, ...]]]

else:
    StyleSpec = object  # type:ignore


class StyledWidget(Widget):

    _build_style_attrs_: StyleSpec = {}
    _stateful_style_attrs_: StyleSpec = {}

    _all_style_attr_names_: set[str]

    # --- typing ---
    _impl_cache_: Any

    # --- impl tie-in defined in subclass ---
    _impl_build_: ClassVar[Callable]  # type: ignore
    _impl_set_size_: ClassVar[Callable]  # type: ignore
    _impl_apply_style_: ClassVar[Callable]  # type: ignore

    _theme_: InheritedAttribute[Theme] = LazyInheritedAttribute("_theme_", None)

    def __init__(self, style=None, _margin_=None, **kwargs):

        buildatters = {
            name: kwargs[name]
            for name in kwargs
            if self._allows_themed_build_attr_(name)
        }

        statefulattrs = {
            name: kwargs[name]
            for name in kwargs
            if self._allows_themed_stateful_attr_(name)
        }

        assert (
            len(overlap := set(buildatters) & set(statefulattrs)) == 0
        ), f"conflicting themedattribute for arguments {overlap}... How!?"

        assert (
            len(extra := set(kwargs) - set(buildatters) - set(statefulattrs)) == 0
        ), f"widget of type '{type(self).__name__}' unexpected/extra keyword arguments {extra}"

        self._build_attrs_ = buildatters
        self._stateful_attrs_ = statefulattrs
        self._theme_ = None

        self._impl_cache_ = None

        super().__init__(_margin_=_margin_)

    def _build_(self, dim_spec):

        # print(self, self._theme_)

        # print(self._all_style_attr_names_)
        attrs = {
            name: getattr(self, name)
            for name in self._all_style_attr_names_
            if self._allows_themed_build_attr_(name)
        }
        # print(attrs)

        # print(self._impl_build_, type(self)._impl_build_.__module__)
        self._native_, suggested_size = self._impl_build_(**attrs)

        spcw, spch = self._specify_dim_spec(dim_spec)

        sgw, sgh = suggested_size

        size = w, h = (
            sgw if self._use_sug_width_ and sgw is not None else spcw,
            sgh if self._use_sug_height_ and sgh is not None else spch,
        )
        # print(
        #     "_build_",
        #     self,
        #     f"size={size}",
        #     (self._use_sug_width_, self._use_sug_heigh
        # t_),
        # )
        super()._build_(size)

        self._impl_set_size_(self._native_, w, h)

        assert self._native_ is not None

        # --- register style states ---
        # there are three scenearios, State[Style], Style(state), Style
        style = self._stateful_attrs_

        if isinstance(style, DerivedStyle):
            handler = self._apply_style_handler
            style._register_handler_(self, handler)
            handler(style)
        else:  # is a Style Object
            self._apply_style_handler(style)
            self._stateful_attrs_ = "_style_removed_after_use_"

    def _demolish_(self):
        if isinstance(self._stateful_attrs_, State):
            self._stateful_attrs_._deregister_handler_(self)
        super()._demolish_()

    def _apply_style_handler(self, style=None):

        attrs = {
            name: getattr(self, name)
            for name in self._all_style_attr_names_
            if self._allows_themed_stateful_attr_(name)
        }

        self._impl_apply_style_(self._native_, **attrs)

    @classmethod
    def _allows_themed_build_attr_(cls, name: str) -> bool:
        return (
            isinstance(attr := getattr(cls, name, None), ThemedAttribute)
            and not attr._stateful
        )

    @classmethod
    def _allows_themed_stateful_attr_(cls, name: str) -> bool:
        return (
            isinstance(attr := getattr(cls, name, None), ThemedAttribute)
            and attr._stateful
        )


def themedwidget(widcls: "Type['Widget']") -> "Type['Widget']":

    assert issubclass(
        widcls, StyledWidget
    ), f"{widcls} does not subclass {StyledWidget}, cannot use @themedwidget on non-styled widget"

    buildattrs = widcls._build_style_attrs_
    statefulattrs = widcls._stateful_style_attrs_

    assert buildattrs not in (
        matched_build_conflict := cls
        if (buildattrs is cls._build_style_attrs_)
        else False
        for cls in Theme._required_
    ), (
        f"{widcls} missing the ._build_style_attrs_ class attribute, "
        + "@themedwidget classes require ._build_style_attrs_ attrs spec. "
        + f"(ie found a dict that belongs to {matched_build_conflict})"
    )

    assert not any(
        matched_stateful_conflict_dicts := (
            cls if (statefulattrs is cls._stateful_style_attrs_) else False
            for cls in Theme._required_
        )
    ), (
        f"{widcls} missing the ._stateful_style_attrs_ class attribute, "
        + "@themedwidget classes require ._stateful_style_attrs_  attrs spec. "
        + f"(ie found a dict that belonges to {matched_stateful_conflict_dicts})"
    )

    assert (
        len(
            overlap := set(widcls._build_style_attrs_)
            & set(widcls._stateful_style_attrs_)
        )
        == 0
    ), f"overlapping build and stateful style attributes {overlap} in {widcls}"

    for attr, allowed in buildattrs.items():
        setattr(widcls, attr, ThemedAttribute(attr, False, widcls, allowed))

    for attr, allowed in statefulattrs.items():
        setattr(widcls, attr, ThemedAttribute(attr, True, widcls, allowed))

    Theme._required_.add(widcls)

    widcls._all_style_attr_names_ = {
        attr
        for attr in dir(widcls)
        if isinstance(getattr(widcls, attr, None), ThemedAttribute)
    }

    return widcls


if TYPE_CHECKING:
    themedwidget = lambda cls: cls

# setup base internal state

themedwidget(StyledWidget)
