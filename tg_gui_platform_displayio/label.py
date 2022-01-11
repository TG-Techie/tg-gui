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

from displayio import Group
from tg_gui_core import Color, State, align
from .shared import decorator_pass as _decorator_pass

from adafruit_display_text import LabelBase
from adafruit_display_text.label import Label as GlyphLabel
from adafruit_display_text.bitmap_label import Label as BitmapLabel
from terminalio import FONT

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type

    from ... import Label, align
    from .. import SizeHint


format_class = _decorator_pass


def build(
    widget: Label,
    *,
    size: float | int,
    align: align,
    fit_to: bool | str,
) -> tuple[Group, SizeHint]:

    assert isinstance(size, int), (
        "for now, text size on circuitpython must be an "
        + f"int, found object of type {type(size).__name__} with value size={size}"
    )

    is_state = isinstance(widget._text, str)

    LabelType: Type[LabelBase] = BitmapLabel if is_state else GlyphLabel
    kwargs = {"save_text": False} if is_state else {}

    # print(
    #     widget,
    #     widget.text,
    # )
    native_label: LabelBase = LabelType(
        font=FONT,
        text=fit_to if isinstance(fit_to, str) else widget.text,
        scale=size,
        **kwargs,
    )

    native = Group()
    native.append(native_label)

    widget._impl_cache_ = (size, align)

    margin = widget._margin_

    # w, h = (
    #     native_label.bounding_box[2],
    #     native_label.bounding_box[3],
    # )

    # print(
    #     widget,
    #     w / len(widget.text),
    #     (w, h),
    # ),
    return (
        native,
        (
            int(1.15 * native_label.bounding_box[2] * size) + margin * 2,
            int(1.15 * native_label.bounding_box[3] * size) + margin * 2,
        ),
    )


def set_size(widget: Label, native: Group, width: int, height: int) -> None:
    """
    A tie-in to set the size of the native element based on the size hint and fixed style
    :param widget:
    :param width:
    :param height:
    """

    native_label: LabelBase = native[0]
    size: int

    (size, lbl_align) = widget._impl_cache_
    margin = widget._margin_

    widw, widh = width, height
    del width, height  # safety del

    _, _, lblw, lblh = native_label.bounding_box
    lblw *= size
    lblh *= size

    # print("set_size", widget, lblw / len(widget.text), (lblw, lblh), (widw, widh))

    y = widh // 2
    if lbl_align is align.center:
        x = (widw - lblw) // 2
    elif lbl_align is align.leading:
        x = 0
    elif lbl_align is align.trailing:
        x = widw - lblw
    else:
        assert False, f"unknown alignment for label {widget}, found {lbl_align}"

    native_label.x = x + margin
    native_label.y = y + margin


def apply_style(
    widget: Label,
    native: Group,
    *,
    color: Color,
) -> None:
    """
    formats the native widget with style attribute given.
    These are defined in the _stateful_style_attrs_ in the std class.
    :param widget: the tg-gui widget instance
    :param native: the imple native element to apply style to
    :param **style_attrs: the stateful style attributes being applied
    :return: nothing
    """
    native[0].color = color


def set_text(widget: Label, text: str):
    """
    changes the text of native element
    """
    widget._native_[0].text = text
