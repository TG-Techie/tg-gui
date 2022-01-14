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

import displayio
from tg_gui_core import *
from tg_gui_core import _Screen_

from .event_loop import EventLoop

import gc
from gc import collect as gc_collect
from time import monotonic_ns

import microcontroller
import sys

from displayio import Group, Display

if not isoncircuitpython():
    from typing import Protocol


class Screen(_Screen_):
    display: Display
    touch_loop: EventLoop
    root: Root

    __circuitpy_attr_tag = None

    def __init__(
        self,
        *,
        display: Display,
        loop: EventLoop,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.display = display
        self.touch_loop = loop

    def run(self):
        assert self.root._native_ is not None
        self.display.auto_refresh = False
        self.display.show(self.root._native_)

        # raise RuntimeError()

        print("Current widget tree:")
        self.root._print_tree(fn=lambda w: (w.coord, w.dims, w.isshowing()))

        print("setting up recurring updates...")
        now = monotonic_ns()
        sort = lambda pack: pack[2]
        updates = sorted(
            (
                [fn, int(period * 1e9), now + int(period * 1e6)]
                for fn, period in self._iter_registered_updates_()
            ),
            key=sort,
        )

        # run each event first
        for (fn, _, _) in updates:
            fn()

        gc_collect()
        print(gc.mem_free())
        print("starting loop...")
        touch_loop = self.touch_loop

        display_refresh = self.display.refresh

        loop = touch_loop.loop

        while True:
            display_refresh()
            loop()
            display_refresh()
            loop()
            display_refresh()
            loop()
            gc_collect()

            # run_updates
            now = monotonic_ns()
            for (pack, (fn, period, run_next)) in zip(updates, updates):
                if run_next < now:
                    fn()
                    pack[2] = now + period
                else:
                    break
            updates.sort(key=sort)
            # # if len(rotate) != len(updates):
            # for _ in range(rotate):
            #     updates.append(updates.pop(0))

    def on_root_set(self, root: Root) -> None:
        pass

    def on_widget_nest_in(_, widget: Widget):
        pass  # raise NotImplementedError

    def on_widget_unnest_from(_, widget: Widget):
        pass  # raise NotImplementedError

    def on_widget_build(_, widget: Widget):
        pass
        # else:
        #     print(f"WARNING?: widget {widget} has no _native_ element")

    def on_widget_demolish(self, widget: Widget):
        raise NotImplementedError()

    def on_widget_place(self, widget: Widget):
        widget._native_.x, widget._native_.y = widget._rel_coord_

    def on_widget_pickup(self, widget: Widget):
        raise NotImplementedError()

    def on_widget_show(self, widget: Widget):
        self.touch_loop.add_widget_if_needed(widget)
        if widget._native_ is not None:
            assert widget._superior_ is not None
            assert widget._superior_._native_ is not None
            widget._superior_._native_.append(widget._native_)
        else:
            print(f"WARNING?: widget {self} has no native element")

    def on_widget_hide(self, widget: Widget):
        self.touch_loop.remove_widget_if_present(widget)
        if widget._native_ in widget._superior_._native_:
            widget._superior_._native_.remove(widget._native_)

    # container tie-ins
    def on_container_build(_, widget: Widget):
        assert widget._native_ is None
        widget._native_ = group = Group()
        group.hidden = False

    def on_container_demolish(_, widget: Widget):
        raise NotImplementedError()

    def on_container_place(_, widget: "Widget"):
        group: Group = widget._native_
        group.x, group.y = widget._rel_coord_

    def on_container_pickup(_, widget: "Widget"):
        raise NotImplementedError

    def on_container_show(_, widget: Widget, _full_refresh=False):
        group: Group = widget._native_
        group.hidden = False
        # raise RuntimeError()

    def on_container_hide(_, widget: Widget):
        group: Group = widget._native_
        group.hidden = True
