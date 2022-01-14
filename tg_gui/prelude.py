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
from ._platform_ import Screen, prelude as _prelude_impl

try:
    from typing import Callable, ClassVar, Any
except:
    pass

# --- setup and globals ---


def main(
    screen: Screen,
    size: None | tuple[int, int] = None,
    _startup: bool = True,
) -> Callable[[Widget], Widget]:

    rootwid = Root(
        screen=screen,
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

# from tg_gui_core.container import superior, app


class default:
    def __init__(self) -> None:
        raise TypeError("cannot create instances of default")

    screen: ClassVar[Callable[..., Screen]] = staticmethod(_prelude_impl.default_screen)


# --- tg_gui_core interface ---
from tg_gui_core import *

# --- tg_gui_platform interface ---
from .button import Button
from .label import Label

# --- tg_gui interface ---
from .layoutstack import VStack, HStack

from .date import Date

from .view import View
