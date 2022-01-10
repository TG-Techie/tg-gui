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

from tg_gui_core import *
from tg_gui_core import _Screen_

import sys

from __feature__ import snake_case, true_property  # type: ignore

from PySide6.QtWidgets import QApplication, QMainWindow, QWidget
from PySide6.QtCore import QRect, QPoint, Qt, QSize, QTimer
from PySide6.QtGui import QCloseEvent


def _create_timer(fn, period: int) -> QTimer:
    timer = QTimer()

    def _update_cycle():
        timer.stop()
        fn()
        timer.start(period)

    timer.timeout.connect(_update_cycle)
    timer.start(period)
    return timer


class Screen(_Screen_):
    def __init__(self, *args, **kwargs):
        _Screen_.__init__(self, *args, **kwargs)
        self.app = QApplication(sys.argv)
        self.native_root = QMainWindow()

    def run(self):
        # setup update functions

        timers = []
        for fn, period in self._iter_registered_updates_():

            timers.append(_create_timer(fn, int(period * 1000)))

        sys.exit(self.app.exec())

    def on_root_set(self, root):
        pass

    def on_widget_nest_in(_, widget: Widget):
        pass  # raise NotImplementedError

    def on_widget_unnest_from(_, widget: Widget):
        pass  # raise NotImplementedError

    def on_widget_build(self, widget: Widget):
        # print("on_widget_build", widget, widget._superior_, widget._native_ is not None)
        if widget._native_ is not None:
            widget._native_.set_parent(widget._superior_._native_)

    def on_widget_demolish(self, widget: Widget):
        widget._native_ = None

    def on_widget_place(self, widget: Widget):
        # print(f"on_widget_place", widget)
        native = widget._native_
        if native is not None:
            x, y = widget._rel_coord_
            native.pos = QPoint(x, y)
            native.size = QSize(*widget._phys_size_)

    def on_widget_pickup(self, widget: Widget):
        # print(f"{self}.on_widget_place(widget={widget})")
        pass

    def on_widget_show(self, widget: Widget):
        if widget._native_ is not None:
            widget._native_.show()

    def on_widget_hide(self, widget: Widget):
        if widget._native_ is not None:
            widget._native_.hide()

    # container tie-ins
    def on_container_build(_, widget: Widget):
        widget._native_ = native = QWidget()
        superior = widget._superior_

        if superior is not None:
            native.set_parent(superior._native_)

    def on_container_demolish(_, widget: Widget):
        widget._native_ = None

    def on_container_place(_, widget: "Widget"):
        # if widget._native_ is not None:
        assert (
            widget._native_ is not None
        ), f"{widget} was probably not built w/ on_container_build (._native_)"
        x, y = widget._rel_coord_
        widget._native_.pos = QPoint(x, y)
        widget._native_.size = QSize(*widget._phys_size_)

    def on_container_pickup(_, widget: "Widget"):
        raise NotImplementedError

    def on_container_show(_, widget: Widget, _full_refresh=False):
        widget._native_.show()

    def on_container_hide(_, widget: Widget):
        widget._native_.hide()
