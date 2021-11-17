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

from tg_gui_core import Widget, isoncircuitpython, UID
import time
from time import monotonic_ns
from micropython import const  # type: ignore

_do_nothing = lambda: None


if not isoncircuitpython():
    from typing import Callable, Optional, Protocol

    Time = int
    # --- known import fail ---
    try:  #  typing import hack
        Point = tuple[int, int]
        # from .screen import Screen

        class Selectable(Widget, Protocol):  # type: ignore
            def _select_(self) -> None:
                ...

            def _deselect_(self) -> None:
                ...

        class Pressable(Widget, Protocol):  # type: ignore
            def _action_(self) -> None:
                ...

        class Updateable(Widget, Protocol):  # type: ignore
            def _start_update_(self, coord: Point) -> None:
                ...

            def _continue_update_(self, coord: Point) -> None:
                ...

            def _end_update_(self, coord: Point) -> None:
                ...

        class EventLoop(Protocol):
            def wastocuhed(self) -> bool:
                ...

            @property
            def touchedcoord(self) -> Optional[Point]:
                ...

            def loop(self) -> None:
                ...

            def add_widget_if_needed(self, widget: Widget):
                ...

            def remove_widget_if_present(self, widget: Widget):
                ...

    except:
        pass

else:
    EventLoop = object  # type:ignore


def adjust_phys_to_rel(ref_wid: Widget, coord: Point) -> Point:
    x, y = coord
    px, py = ref_wid._phys_coord_
    return (x - px, y - py)


# #@micropython.native
def has_phys_coord_in(
    widget: Widget,
    coord: tuple[int, int],
    _print: bool = False,
) -> bool:
    #
    minx, miny = widget._phys_coord_
    x, y = coord
    maxx, maxy = widget._phys_end_coord_
    return (minx <= x <= maxx) and (miny <= y <= maxy)


"""
There are four modes for action that is taken on input:
- nothing found
- pressable found
- horizontal updateable found
- vertical updateable found
for now we will stick with just one updateable.
"""

_NOTHING_MODE = const(1)
_PRESS_MODE = const(2)
_UPDATE_MODE = const(3)


def isselectable(widget: Widget | Selectable) -> bool:
    return hasattr(widget, "_select_") and hasattr(widget, "_deselect_")  # type: ignore


def ispressable(widget: Widget | Pressable) -> bool:
    return hasattr(widget, "_action_") and callable(widget._action_)  # type: ignore


def isupdateable(widget: Widget | Updateable) -> bool:
    return (
        hasattr(widget, "_start_update_")
        and hasattr(widget, "_continue_update_")
        and hasattr(widget, "_end_update_")
    )  # type: ignore


class SinglePointEventLoop(EventLoop):
    def wastouched(self) -> bool:
        return self._is_touched

    @property
    def touchedcoord(self) -> Optional[Point]:
        return self._coord if self._is_touched else None

    def __init__(
        self,
        poll_coord: Callable[[], None | Point],
        *,
        scroll_threshold: int = 15,
    ) -> None:
        # setup / config
        self.poll_coord = poll_coord
        self.scroll_threshold = scroll_threshold

        # -- found widget states ---
        self._mode = _NOTHING_MODE
        self._selected: None | Selectable = None
        self._pressable: None | Pressable = None
        self._updateable: None | Updateable = None

        # -- coord states ---
        self._coord: Point = (-0x1701D, -0x1701D)
        self._is_touched: bool = True

        self._last_coord: Point = (-0x1701D, -0x1701D)
        self._was_touched: Point = (-0x1701D, -0x1701D)

        # for UPDATE == start coord for scrollabe / updateable widgets
        self._start_coord: Point = (-0x1701D, -0x1701D)

        # interface / lists to store the widgets to inspect
        self._selectbles_: dict[UID, Selectable] = {}
        self._pressables_: dict[UID, Pressable] = {}
        self._updateables_: dict[UID, Updateable] = {}

    def add_widget_if_needed(self, widget: Widget):
        wid_id = widget._id_
        if isselectable(widget):
            self._selectbles_[wid_id] = widget  # type: ignore
        if ispressable(widget):
            self._pressables_[wid_id] = widget  # type: ignore
        if isupdateable(widget):
            self._updateables_[wid_id] = widget  # type: ignore

    def remove_widget_if_present(self, widget: Widget):
        wid_id = widget._id_
        if wid_id in (selectables := self._selectbles_):
            selectables.pop(wid_id)
        if wid_id in (pressables := self._pressables_):
            pressables.pop(wid_id)
        if wid_id in (updateables := self._updateables_):
            updateables.pop(wid_id)

    def loop(self):
        global monotonic_ns

        now = monotonic_ns()
        assert isinstance(now, int), f"now={repr(now)}"

        # get previous data
        was_touched = self._was_touched
        last_coord = self._last_coord

        # get current data
        self._coord = coord = self.poll_coord()
        self._is_touched = is_touched = coord is not None

        if is_touched and not was_touched:
            # print(f"[down] coord={coord}, last_coord={last_coord}")
            self._touch_down()
        elif not is_touched and was_touched:
            # print(f"[ up ] coord={coord}, last_coord={last_coord}")
            self._touch_up()
        elif is_touched:
            # print(f"[cont] coord={coord}, last_coord={last_coord}")
            self._continue_touch()
        elif not is_touched and not was_touched:
            pass
        else:
            assert False, "unreachable"

        self._last_coord = coord
        self._was_touched = is_touched

        del self._coord
        del self._is_touched

    def _touch_down(self) -> None:
        coord = self._coord
        # scan thought all pointable.selectable widgets then the actionable ones
        for selectable in self._selectbles_.values():
            # if the point being touched is in the widget
            if has_phys_coord_in(selectable, coord):
                # select then store the widget
                selectable._select_()
                self._selected = selectable
                break

        # scan the actionables
        for pressable in self._pressables_.values():
            if has_phys_coord_in(pressable, coord):
                self._pressable = pressable
                break
        # else:
        #     pressable = None # type: ignore , here for filtering out buts

        for updateable in self._updateables_.values():
            if has_phys_coord_in(selectable, coord, _print=True):
                updateable._start_update_(adjust_phys_to_rel(selectable, coord))
                self._updateable = updateable
                break

        self._mode = _NOTHING_MODE if pressable is None else _PRESS_MODE
        self._start_coord = coord

    def _continue_touch(self) -> None:
        mode = self._mode
        updateable = self._updateable
        if updateable is not None:
            if mode != _UPDATE_MODE:
                start_x, start_y = self._start_coord
                now_x, now_y = self._coord
                threshold = self.scroll_threshold

                diff_x = start_x - now_x
                diff_y = start_y - now_y

                if abs(diff_x) >= threshold or abs(diff_y) >= threshold:
                    self._mode = mode = _UPDATE_MODE

            elif mode == _UPDATE_MODE:
                updateable._continue_update_(
                    adjust_phys_to_rel(updateable, self._coord)
                )

    def _touch_up(self) -> None:
        mode = self._mode
        if (selected := self._selected) is not None:
            selected._deselect_()
            self._selected = None

        if (
            mode == _PRESS_MODE
            and (pressable := self._pressable) is not None
            and has_phys_coord_in(pressable, self._last_coord)
        ):
            pressable._action_()
            self._pressable = None

        # TODO: figure out and docuemtn why this does not have a mode check
        if (updateable := self._updateable) is not None:

            updateable._end_update_(adjust_phys_to_rel(updateable, self._last_coord))
            self._updateable = None
