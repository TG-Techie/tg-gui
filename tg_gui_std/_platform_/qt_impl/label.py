from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel
from PySide6.QtGui import QFontMetrics, QFont
from .shared import to_qt_color, to_qt_font_size, to_alignment_lookup

from __feature__ import snake_case, true_property

format_class = lambda cls: cls


def build(widget, *, size, align):
    native = QLabel(widget.text)

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
        "QLabel {" f"color:{to_qt_color(color)}; {widget._impl_cache_}" "}"
    )


def set_text(widget, text):
    widget._native_.text = text
