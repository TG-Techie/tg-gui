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

from PySide6 import QtCore, QtWidgets, QtGui
from PySide6.QtCore import Qt

from tg_gui_core import align

Native = QtWidgets.QWidget


def to_qt_font_size(size):
    return f"{round(size*20)}px"


def to_qt_color(color):
    clr = hex(color)[2:]
    while len(clr) < 6:
        clr = "0" + clr

    return f"#{clr}"


to_alignment_lookup = {
    align.center: Qt.AlignCenter,
    align.leading: Qt.AlignLeading,
    align.trailing: Qt.AlignTrailing,
}

# def clickable(widget):
#     class Filter(QtCore.QObject):
#         clicked = QtCore.Signal()
#
#         def eventFilter(self, obj, event):
#             if obj == widget:
#                 if event.type() == QtCore.QEvent.MouseButtonRelease:
#                     if obj.rect().contains(event.pos()):
#                         self.clicked.emit()
#                         # The developer can opt for .emit(obj) to get the object within the slot.
#                         return True
#             return False
#
#     filter = Filter(widget)
#     widget.installEventFilter(filter)
#     return filter.clicked
