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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import *

    from .theming import Theme

    Native = Any


class StyledWidget(Widget):
    # --- typing ---
    _impl_cache_: Any
    _style_: None | Style

    # --- class interface ---

    # user facing style
    _stateful_style_attrs_: ClassVar[set[str] | dict[str, Any]]
    _fixed_style_attrs_: ClassVar[set[str] | dict[str, Any]]

    # --- impl tie-in defined in subclass ---
    _impl_build_: ClassVar[Callable]  # type: ignore
    _impl_set_size_: ClassVar[Callable]  # type: ignore
    _impl_apply_style_: ClassVar[Callable]  # type: ignore

    _theme_: Theme = property(lambda self: self._superior_._theme_)  # type: ignore

    def __init__(self, style=None, **kwargs):
        super().__init__(margin=kwargs.pop("margin", None))

        # check that the kwargs only contain fixed styling info
        fixed = self._fixed_style_attrs_
        assert all(kwarg in fixed for kwarg in kwargs), (
            f"unexpected keyword(s) passed to `{type(self).__name__}"
            + f"({', '.join(unexpected+'=' for unexpected in set(kwargs) - fixed)})`"
        )

        # # check that kwargs is a subset of _fixed_style_attrs_
        # fixed_style_attrs = self._fixed_style_attrs_

        self._fixed_styling = kwargs
        self._impl_cache_ = None
        self._style_ = style

    def _on_nest_(self):
        super()._on_nest_()

        style = self._style_
        if style is None:
            self._style_ = self._superior_._theme_.get_styling_for(type(self))["style"]
        elif isinstance(style, Style):
            style._configure_(self)
        else:
            assert isinstance(style, dict), (
                f"{self} expected a dict or Style style object for "
                + f"the style= parameter, found {style}"
            )

    def _build_(self, dim_spec):
        defaults = self._superior_._theme_.get_styling_for(type(self))

        # # suggested_size = self._impl_suggest_size_()
        # super()._build_(dim_spec)

        # filler for now
        fixed = self._fixed_styling

        self._native_, suggested_size = self._impl_build_(
            **{
                key: specify(fixed.get(key, defaults[key]), self)
                for key in self._fixed_style_attrs_
            }
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
        del fixed, self._fixed_styling

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
