import displayio
from tg_gui_core import *
from tg_gui_core import _Screen_

from .event_loop import EventLoop

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
        self.display.show(self.root._native_)

        # raise RuntimeError()

        print("Current widget tree:")
        self.root._print_tree(fn=lambda w: (w.coord, w.dims, w.isshowing()))

        print("starting loop...")
        touch_loop = self.touch_loop

        done = False

        while True:
            touch_loop.loop()

        # self.root._print_tree(
        #     fn=lambda w: (
        #         w.coord,
        #         w.dims,
        #         repr(n := w._native_),
        #         len(n),
        #         (n.x, n.y),
        #         n.hidden,
        #     )
        # )

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
        # TODO: NEXT: figure out why .on_container_show is not being called
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