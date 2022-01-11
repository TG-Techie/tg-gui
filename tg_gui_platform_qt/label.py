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

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFontMetrics, QFont
from .shared import to_qt_color, to_qt_font_size, to_alignment_lookup

from __feature__ import snake_case, true_property  # type: ignore


format_class = lambda cls: cls


def build(widget, *, size, align, fit_to: bool | str):
    native = QLabel(fit_to if isinstance(fit_to, str) else widget.text)

    native.alignment = to_alignment_lookup[align]
    native.style_sheet = (
        widget._impl_cache_
    ) = f"font-size: {to_qt_font_size(size)}; padding: 5px;"

    w, h = native.size_hint().to_tuple()
    return (
        native,
        (1.2 * w // 1, h),
        # (QFontMetrics.horizontal_advance(widget.text), native.size_hint().height),
    )


def set_size(widget, native: QLabel, width: int, height: int) -> None:
    """
    A tie-in to set the size of the native element based on the size hint and fixed style
    :param widget:
    :param width:
    :param height:
    """
    pass  # TODO: evaluate if this should be pass for qt (and done in screen) or here


def apply_style(widget, native, *, color):
    native.style_sheet = sheet = (
        "QLabel {" + f"color:{to_qt_color(color)}; {widget._impl_cache_}" + "}"
    )


def set_text(widget, text):
    widget._native_.text = text
