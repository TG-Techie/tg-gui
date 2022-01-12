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


from tg_gui_core import Color

from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Slot

from .shared import to_qt_color, to_qt_font_size, Native

from __feature__ import snake_case, true_property  # type: ignore

try:
    from typing import Type, Union
    from .. import SizeHint
    from ... import Button
except:
    pass

format_class = lambda cls: cls


def build(
    widget: Button,
    *,
    radius: int,
    size: int | float,
    fit_to_text: bool,
) -> tuple[Native, SizeHint]:
    native = QPushButton(widget._text)

    native.clicked.connect(widget._action_)

    native.style_sheet, _ = widget._impl_cache_ = (
        f"font-size:{to_qt_font_size(size)};",
        lambda: f"border-radius:{min(radius, min(widget._phys_size_) // 2)}px;",
    )

    # None for now, later will use disposition
    return (native, native.size_hint().to_tuple())


def set_size(widget: Button, native: Native, width: int, height: int) -> None:
    """
    A tie-in to set the size of the native element based on the size hint and fixed style
    :param widget:
    :param width:
    :param height:
    """
    pass  # set in Sreen class
    # TODO: evaluate if qt_impl .set_size funcs should be pass or not


def apply_style(
    widget: Button,
    native: Native,
    *,
    fill: Color,
    foreground: Color,
    active_fill: Color,
    active_color: Color,
):
    imple_str = widget._impl_cache_
    if isinstance(imple_str, tuple):
        base, fn = imple_str
        imple_str = widget._impl_cache_ = base + fn()

    native.style_sheet = sheet = (
        "QPushButton {"
        + f"background-color: {to_qt_color(fill)}; color: {to_qt_color(foreground)}; {imple_str}"
        + "} QPushButton:pressed {"
        + f"background-color: {to_qt_color(active_fill)}; color: {to_qt_color(active_color)};"
        + "}"
    )


# possible future features
def suggest_size(widget):
    raise NotImplementedError()


def etc():
    raise NotImplementedError()
