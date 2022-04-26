from __future__ import annotations

import sys

from tg_gui.core import Pixels, RootWidget, platform_support

from PySide6 import QtCore, QtGui, QtWidgets

NativeElement = QtWidgets.QWidget
NativeContainer = QtWidgets.QWidget
NativeRootContainer = QtWidgets.QWidget


class Platform(platform_support._Platform_):
    def __init__(self) -> None:
        self._app = QtWidgets.QApplication([])
        self._window = QtWidgets.QMainWindow()
        self._central_qtwidget: NativeRootContainer

    def run(self) -> None:
        self._window.show()
        self._app.exec_()

    @classmethod
    def default(cls) -> Platform:
        return cls()

    @property
    def native_root(self) -> NativeRootContainer | None:
        return getattr(self, "_central_qtwidget", None)

    def default_size(self) -> tuple[Pixels, Pixels]:
        return (800, 600)

    def new_container(self, dimensions: tuple[Pixels, Pixels]) -> NativeContainer:
        """
        Returns an empty widget with the given dimensions.
        """
        widget = NativeContainer()
        widget.setFixedSize(dimensions[0], dimensions[1])
        return widget

    def init_native_root_container(
        self,
        dimensions: tuple[Pixels, Pixels],
    ) -> NativeRootContainer:
        """
        Returns an empty widget with the given dimensions and set it as the central widget
        in the application
        """
        if getattr(self, "_central_qtwidget", None) is not None:
            return self._central_qtwidget
        else:
            # make the central widget
            self._central_qtwidget = widget = QtWidgets.QWidget()
            widget.setFixedSize(dimensions[0], dimensions[1])
            self._window.setCentralWidget(widget)
            self._window.setFixedSize(dimensions[0], dimensions[1])
            return widget

    def nest_element(
        self,
        container: NativeContainer,
        element: NativeElement,
    ) -> NativeContainer:
        """
        Adds the given element to the container and returns the container.
        """
        element.setParent(container)
        return container

    def unnest_element(
        self,
        container: NativeContainer,
        element: NativeElement,
    ) -> None:
        """
        Removes the given element from the container.
        """
        container.layout().removeWidget(element)

    def set_relative(
        self,
        container: NativeContainer,
        element: NativeElement,
        position: tuple[Pixels, Pixels],
    ) -> None:
        """
        Sets the position of the element relative to the container.
        """
        element.move(position[0], position[1])

    def show_element(self, element: NativeElement) -> None:
        """
        Shows the given element.
        """
        element.show()

    def hide_element(self, element: NativeElement) -> None:
        """
        Hides the given element.
        """
        element.hide()
