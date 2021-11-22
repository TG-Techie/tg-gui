from displayio import Group
from tg_gui_core import Color, State, align
from .shared import decorator_pass as _decorator_pass

from adafruit_display_text import LabelBase
from adafruit_display_text.label import Label as GlyphLabel
from adafruit_display_text.bitmap_label import Label as BitmapLabel
from terminalio import FONT

try:
    from typing import Type

    from ... import Label, align
    from .. import SizeHint

    Native = object  # repalce with displayio later
except:
    pass


format_class = _decorator_pass


def build(
    widget: Label,
    *,
    size: float | int,
    align: align,  # type: ignore
) -> tuple[Native, SizeHint]:

    assert isinstance(size, int), (
        "for now, text size on circuitpython must be an "
        + f"int, found object of type {type(size).__name__} with value size={size}"
    )

    is_state = isinstance(widget._text, str)

    LabelType: Type[LabelBase] = BitmapLabel if is_state else GlyphLabel
    kwargs = {"save_text": False} if is_state else {}

    native_label: LabelType = LabelType(
        font=FONT,
        text=widget.text,
        scale=size,
        **kwargs,
    )

    native = Group()
    native.append(native_label)

    widget._impl_cache_ = (size, align)

    margin = widget._margin_

    return (
        native,
        (
            None if is_state else native_label.bounding_box[2] + margin * 2,
            native_label.bounding_box[3] + margin * 2,
        ),
    )


def set_size(widget: Label, native: Native, width: int, height: int) -> None:
    """
    A tie-in to set the size of the native element based on the size hint and fixed style
    :param widget:
    :param width:
    :param height:
    """

    native_label: LabelBase = native[0]
    size: int

    (size, lbl_align) = widget._impl_cache_

    m = widget._margin_

    widw, widh = width - m * 2, height - m * 2
    del width, height  # safety del

    _, _, lblw, lblh = native_label.bounding_box
    lblw = lblw + m * 2
    lblh = lblh + m * 2

    y = widh // 2
    if lbl_align is align.center:
        x = (widw - lblw) // 2
    elif lbl_align is align.leading:
        x = 0
    elif lbl_align is align.trailing:
        x = widw - lblw
    else:
        assert False, f"unknown alignment for label {widget}, found {lbl_align}"

    native_label.x = x + m
    native_label.y = y + m


def apply_style(
    widget: Label,
    native: Native,
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
