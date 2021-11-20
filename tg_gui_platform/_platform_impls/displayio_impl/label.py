from tg_gui_core import Color
from .shared import decorator_pass as _decorator_pass

from adafruit_display_text.label import Label

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
    """
    Creates the native element for the std tg-gui widget based on the _fixed_style_attrs_.
    Those _fixed_style_attrs_ are passed as kwargs to this function.
    :param widget: the tg-gui widget instance to build the native for
    :param **style_attrs: the fixed style attributes that are set at build time
    :return: a tuple of the native widget and suggested size
    """
    raise NotImplementedError()


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
    raise NotImplementedError()


def set_size(widget, native: QLabel, width: int, height: int) -> None:
    """
    A tie-in to set the size of the native element based on the size hint and fixed style
    :param widget:
    :param width:
    :param height:
    """
    raise NotImplementedError()


def set_text(widget: Label, text: str):
    """
    changes the text of native element
    """
    raise NotImplementedError()
