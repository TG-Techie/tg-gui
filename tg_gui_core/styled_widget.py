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

from tg_gui_core import Widget, State, specify, isoncircuitpython

from .style import Style, DerivedStyle
from .theming import Theme, ThemedBuildAttribute, ThemedStatefulAttribute

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import *

    from .theming import Theme

    Native = Any

    StyleSpec = ClassVar[dict[str, type | tuple[type, ...]]]

else:
    StyleSpec = object  # type:ignore



class StyledWidget(Widget):

    _sentinel = object()

    _build_style_attrs_: StyleSpec = {}
    _stateful_style_attrs_: StyleSpec = {}

    _all_build_style_attr_names_: set[str]
    _all_stateful_style_attr_names_: set[str]

    # --- typing ---
    _impl_cache_: Any

    # --- impl tie-in defined in subclass ---
    _impl_build_: ClassVar[Callable]  # type: ignore
    _impl_set_size_: ClassVar[Callable]  # type: ignore
    _impl_apply_style_: ClassVar[Callable]  # type: ignore

    @property
    def _theme_(self) -> Theme:
        return self._superior_._theme_

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
        self._impl_cache_ = None

        super().__init__(_margin_=_margin_)


    def _build_(self, dim_spec):

        print(self, self._theme_)

        getthemeattr = self._theme_.getbuildattr
        getselfattr = self._build_attrs_.get
        sentinel = self._sentinel

        self._native_, suggested_size = self._impl_build_(
           
        )

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
        #     (self._use_sug_width_, self._use_sug_height_),
        # )
        super()._build_(size)

        self._impl_set_size_(self._native_, w, h)

        assert self._native_ is not None

        # --- register style states ---
        # there are three scenearios, State[Style], Style(state), Style
        style = self._style_

        if isinstance(style, DerivedStyle):
            handler = self._apply_style_handler
            style._register_handler_(self, handler)
            handler(style)
        else:  # is a Style Object
            self._apply_style_handler(style)
            self._style_ = "_style_removed_after_use_"

    def _demolish_(self):
        if isinstance(self._style_, State):
            self._style_._deregister_handler_(self)
        super()._demolish_()

    def _apply_style_handler(self, style):
        if isinstance(style, Style):
            style._configure_(self)

        self._impl_apply_style_(self._native_, **style)

    @classmethod
    def _allows_themed_build_attr_(cls, name: str) -> bool:
        descriptor = getattr(cls, name, None)
        return isinstance(descriptor, ThemedBuildAttribute)

    @classmethod
    def _allows_themed_stateful_attr_(cls, name: str) -> bool:
        return isinstance(getattr(cls, name, None), ThemedStatefulAttribute)


def themedwidget(widcls: "Type['Widget']") -> "Type['Widget']":

    assert issubclass(
        widcls, StyledWidget
    ), f"{widcls} does not subclass {StyledWidget}, cannot use @themedwidget on non-styled widget"

    buildattrs = widcls._build_style_attrs_
    statefulattrs = widcls._stateful_style_attrs_

    assert buildattrs not in (
        matched_build_conflict:= cls if (buildattrs is cls._build_style_attrs_) else False for cls in Theme._required_
    ), (
        f"{widcls} missing the ._build_style_attrs_ class attribute, "
        + "@themedwidget classes require ._build_style_attrs_ attrs spec. "
        + f"(ie found a dict that belonges to {matched_build_conflict})"
    )

    assert not any(
         matched_stateful_conflict:= cls if (statefulattrs is cls._stateful_style_attrs_) else False for cls in Theme._required_
    ), (
        f"{widcls} missing the ._stateful_style_attrs_ class attribute, "
        + "@themedwidget classes require ._stateful_style_attrs_  attrs spec. "
        + f"(ie found a dict that belonges to {matched_stateful_conflict})"
    )

    for attr, allowed in buildattrs.items():
        setattr(widcls, attr, ThemedBuildAttribute(attr, widcls, allowed))

    for attr, allowed in statefulattrs.items():
        setattr(widcls, attr, ThemedStatefulAttribute(attr, widcls, allowed))

    Theme._required_.add(widcls)

    widcls._all_build_style_attr_names_ = {attr for attr in dir(widcls) if isinstance(getattr(widcls, attr, None), ThemedBuildAttribute)}
    widcls._all_stateful_style_attr_names_     = {attr for attr in dir(widcls) if isinstance(getattr(widcls, attr, None), ThemedStatefulAttribute)}


    return widcls

if TYPE_CHECKING:
    themedwidget = lambda cls: cls

# setup base internal state

themedwidget(StyledWidget)
