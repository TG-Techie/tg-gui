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

from tg_gui_core import Widget, Root, isoncircuitpython
from .screen import Screen
from .event_loop import EventLoop, SinglePointEventLoop

if not isoncircuitpython():
    from typing import Callable

    if isoncircuitpython():  # typing import hack
        from tg_gui_core import Theme
else:
    pass

from displayio import Display

# --- globals ---
_default_screen: None | Screen = None

# --- interface ---
def default_screen(
    *, display: None | Display = None, touch_loop: None | EventLoop = None
) -> Screen:

    global _default_screen

    # lazily create the screen object
    if _default_screen is not None:
        raise ValueError("default screen() already created")
        # why keep a global reference to the display object when screen() cannot be called twice?
        #

    # automagically find the display object unless teh magic smoke is
    # not present in which case complain to the user dev
    if display is None:
        try:
            from drivers import display  # type: ignore
        except ImportError as err:
            print(f"ERROR:`{type(err).__name__}: {err}`")
            raise RuntimeError(
                "unable to automagically find a display for TG-Gui, no display "
                + "provided to prelude.screen(display=...) and unable to find a "
                + "`drivers` module or a `drivers.display` object"
            )

    if touch_loop is None:
        try:
            from drivers import poll_single_touchpoint

            # TODO: ass driver tie-in for swipe threshhold
            touch_loop = SinglePointEventLoop(poll_single_touchpoint)
        except:
            raise RuntimeError(
                "unable to automagically find touch driver for TG-Gui, no touch_loop "
                + "provided to prelude.screen(touch_loop=...) and unable to find a "
                + "`drivers` module with a poll_single_touchpoint"
            )

    # create said object, and store it
    _default_screen = dflt_screen = Screen(
        display=display,
        loop=touch_loop,
        default_margin=2,
    )

    return dflt_screen


def _generate_default_size_from_screen(screen: Screen) -> tuple[int, int]:
    return (screen.display.width, screen.display.height)


# def main(
#     screen: Screen,
#     theme: Theme,
#     size: None | tuple[int, int] = None,
# ) -> Callable[[Widget], Widget]:

#     display = screen.display
#     rootwid = Root(
#         screen=screen,
#         theme=theme,
#         size=size if size is not None else (display.width, display.height),
#     )

#     def _main_startup(wid: Widget) -> Widget:
#         assert wid._is_app_ is True
#         ret = rootwid(wid)
#         rootwid._std_startup_()
#         return ret

#     return _main_startup
