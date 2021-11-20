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
