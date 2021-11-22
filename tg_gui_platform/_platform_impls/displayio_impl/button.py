"""

TODO: add descripton and copyright

to cover:
- the _select_/_action_ Procotol
- the use of the _impl_cache_ in this particular file
"""

from tg_gui_core import Color
from .shared import decorator_pass as _decorator_pass

from displayio import Group
from adafruit_display_shapes.roundrect import RoundRect
from adafruit_display_text.label import Label
from terminalio import FONT


try:
    from typing import Type, Union
    from .. import SizeHint
    from ... import Button
except:
    pass

from displayio import Group as Native


def format_class(cls: Type[Button]) -> Type[Button]:
    """
    @decorator
    A tie-in to path circuitpython required class attributes / methods

    in circuitpython tg-gui the interface for a clickable is the presence of
    `_select_() -> None`, `_action_() -> None`, and `_deselect_() ->None` mthods.
    this decorator pathces them into the class

    :param cls: the tg-gui class object, to format
    :return: the same class
    """
    global cirpy_button_recolor
    cls._recolor = cirpy_button_recolor  # type: ignore
    cls._select_ = lambda self: self._recolor(True)  # type: ignore
    cls._deselect_ = lambda self: self._recolor(False)  # type: ignore
    return cls


def build(
    widget: Button,
    *,
    radius: int,
    size: float | int,
    fit_to_text: bool,
) -> tuple[Native, SizeHint]:
    """
    Creates the native element for the std tg-gui widget based on the _fixed_style_attrs_.
    Those _fixed_style_attrs_ are passed as kwargs to this function.
    :param widget: the tg-gui widget instance to build the native for
    :param **style_attrs: the fixed style attributes that are set at build time
    :return: a tuple of the native widget and suggested size
    """
    native = Group()

    label = Label(font=FONT, x=0, y=0, text=widget.text, scale=size)
    native.append(label)

    _, _, w, h = label.bounding_box
    w *= size
    h = int(1.15 * h * size)
    r = min(radius, w // 2, h // 2)
    padding = round(1.5 * r)

    widget._impl_cache_ = dict(radius=r, label_width=w)
    return (
        native,
        (
            w + padding + widget._margin_ * 2,
            h + widget._margin_ * 2,
        ),
    )
    # return (
    #     native,
    #     (
    #         w + padding + widget._margin_ * 2,
    #         h + widget._margin_ * 2,
    #     )
    #     if fit_to_text
    #     else (None, None),
    # )


def set_size(widget: Button, native: Native, width: int, height: int) -> None:
    """
    A tie-in to set the size of the native element based on the size hint and fixed style
    :param widget:
    :param width:
    :param height:
    """

    radius: int = widget._impl_cache_["radius"]
    label_width: int = widget._impl_cache_["label_width"]
    margin = widget._margin_

    assert len(native) == 1, len(native)
    label: Label = native[0]
    label.x = (width - label_width) // 2
    label.y = height // 2

    rect = RoundRect(
        margin,  # label.x - rectpadding // 2,
        margin,
        width - 2 * margin,
        height - 2 * margin,
        radius,
        stroke=0,
    )

    native.insert(0, rect)


def apply_style(
    widget: Button,
    native: Native,
    *,
    fill: Color,
    text: Color,
    active_fill: Color,
    active_text: Color,
) -> None:
    """
    formats the native widget with style attribute given.
    These are defined in the _stateful_style_attrs_ in the std class.
    :param widget: the tg-gui widget instance
    :param native: the imple native element to apply style to
    :param **style_attrs: the stateful style attributes being applied
    :return: None
    """
    widget._impl_cache_ = cache = ((fill, text), (active_fill, active_text))

    assert len(native) == 2, len(native)

    rect: RoundRect
    label: Label
    rect, label = native

    rect.fill, label.color = cache[False]


def cirpy_button_recolor(widget: Button, is_selected: bool) -> None:
    """"""
    rect: RoundRect
    label: Label
    rect, label = widget._native_

    # widget._impl_cache_: tuple[tuple[Color, Color], tuple[Color, Color]]
    rect.fill, label.color = widget._impl_cache_[int(is_selected)]