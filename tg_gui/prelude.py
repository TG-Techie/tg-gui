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

from tg_gui_core import Widget, isoncircuitpython
from tg_gui_platform import Theme
from tg_gui_platform import Screen, prelude as _prelude_impl

try:
    from typing import Callable, ClassVar, Any
except:
    pass

# --- setup and globals ---

__default_theme_inst: None | Theme = None


def __make_default_theme() -> Theme:
    global __default_theme_inst

    if __default_theme_inst is not None:
        dflt_theme = __default_theme_inst
    else:
        return Theme(
            margin=5,
            styling={
                StyledWidget: dict(
                    fixed={},
                    stateful={},
                ),
                Button: dict(
                    # eventaully these will be system colors like color.system_midgrnd
                    fixed=dict(
                        radius=100,
                        size=1,
                        fit_to_text=False,
                    ),
                    stateful=dict(
                        fill=0x505050,
                        text=0xFFFFFF,
                        active_fill=0x808080,
                        active_text=0xFFFFFF,
                    ),
                ),
                Label: dict(
                    style=dict(color=0xFFFFFF),
                    fixed=dict(
                        size=1,
                        align=align.center,
                    ),
                ),
            },
        )

        # __default_theme_inst = dflt_theme = Theme(Theme._decld_default_styling_dict)

    return dflt_theme


def main(
    screen: Screen,
    theme: Theme,
    size: None | tuple[int, int] = None,
    _startup: bool = True,
) -> Callable[[Widget], Widget]:

    rootwid = Root(
        screen=screen,
        theme=theme,
        size=(
            size
            if size is not None
            else _prelude_impl._generate_default_size_from_screen(screen)
        ),
    )

    def _main_startup(wid: Widget) -> Widget:
        assert wid._is_app_ is True
        ret = rootwid(wid)
        if _startup:
            rootwid._std_startup_()
        return ret

    return _main_startup


# --- interface ---

from tg_gui_core.container import superior, app


class default:
    def __init__(self) -> None:
        raise TypeError("cannot create instances of default")

    screen: ClassVar[Callable[..., Screen]]
    theme: ClassVar[Callable[[], Theme]]


default.screen = _prelude_impl.default_screen
default.theme = __make_default_theme

# --- tg_gui_core interface ---
from tg_gui_core import *


# --- tg_gui_platform interface ---
from tg_gui_platform.button import Button
from tg_gui_platform.label import Label
from tg_gui_platform import guiexit

# --- tg_gui interface ---
from .layout import Layout
from .vstack import VStack

from .date import Date
