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

import sys

from .base import Widget
from .theming import Theme

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Type, ClassVar
    from .theming import ThemeCompatible


class Container(Widget):
    _nested_: list[Widget]

    # --- class tags ---
    _is_root_: ClassVar[bool] = False
    _is_app_: ClassVar[bool] = False
    _declarable_: bool | ClassVar[bool] = False

    _theme_: None | ThemeCompatible = None

    def __init__(self, theme: ThemeCompatible | None = None) -> None:
        super().__init__(_margin_=0)

        if isinstance(theme, dict) and __debug__:
            theme = Theme(theme, _debug_name_=f"auto:{self}")

        self._nested_ = []
        if theme is not None:
            self._theme_ = theme

    def _nest_(self, widget: Widget) -> None:
        if widget not in self._nested_:
            self._nested_.append(widget)
            widget._nest_in_(self)

    def _unnest_(self, widget: Widget) -> None:
        if widget in self._nested_:
            widget._unnest_from_(self)
        while widget in self._nested_:
            self._nested_.remove(widget)

    def _build_(self, dim_spec) -> None:
        raise NotImplementedError(
            f"{type(self).__name__}._build_(...) not implemented,"
            + " see tg_gui_core/container.py for the template"
        )
        # Template:
        super(Container, self)._build_(dim_spec)
        # container subcless specific form code here
        self._screen_.on_container_build(self)  # platform tie-in

    def _demolish_(self) -> None:
        for widget in self._nested_:
            if widget.isformed():
                widget._deform_()
        super()._demolish_()
        self._screen_.on_container_demolish(self)  # platform tie-in

    def _place_(self, pos_spec) -> None:
        raise NotImplementedError(
            f"{type(self).__name__}._place_(...) not implemented,"
            + " see tg_gui_core/container.py for the template"
        )
        # Template:
        super(Container, self)._place_(pos_spec)
        # container subcless specific place code here
        self._screen_.on_container_place(self)  # platform tie-in

    def _pickup_(self) -> None:
        for widget in self._nested_:
            if widget.isplaced():
                widget._pickup_()
        super()._pickup_()
        self._screen_.on_container_pickup(self)  # platform tie-in

    def _show_(self) -> None:
        super()._show_()
        for wid in self._nested_:
            wid._show_()
        self._screen_.on_container_show(self)

    def _hide_(self):
        for widget in self._nested_:
            if widget.isshowing():
                widget._hide_()
        super()._hide_()
        self._screen_.on_container_hide(self)

    def _print_tree(self, _level=0, **kwargs):
        super()._print_tree(_level=_level, **kwargs)
        _level += 1
        for wid in self._nested_:
            wid._print_tree(_level=_level, **kwargs)
