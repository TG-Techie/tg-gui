from __future__ import annotations

from PySide6.QtWidgets import QLabel
from PySide6.QtCore import QSize

from .shared import NativeElement, NativeContainer
from .._platform_setup_ import *


@widget
# class Text(NativeWidget[QLabel]):
class Text(NativeWidget):

    native: QLabel
    text: str = StatefulAttr(init=True, kw_only=False)

    def onupdate_theme(self, attr: ThemedAttr[Any] | None) -> None:
        """
        called when a dependent themed attribute changes
        """
        raise NotImplementedError

    @onupdate(text)
    def onupdate_text(self, text: str) -> None:
        self.native.setText(text)

    def _build_(
        self, suggestion: tuple[Pixels, Pixels], *, text: str | State[str]
    ) -> tuple[NativeElement, tuple[Pixels, Pixels]]:
        native = QLabel()
        native.setText(self.text)
        native.show()
        native.hide()
        return native, native.sizeHint().toTuple()  # type: ignore

    def _demolish_(self, native: NativeElement) -> None:
        native.destroy()  # TODO: Should this be here?

    def _place_(
        self,
        container: NativeContainer,
        native: NativeElement,
        pos: tuple[Pixels, Pixels],
        abs_pos: tuple[Pixels, Pixels],
    ) -> None:
        native.setParent(container)  # type: ignore
        native.move(x=pos[0], y=pos[1])  # type: ignore

    def _pickup_(
        self,
        container: NativeContainer,
        native: NativeElement,
    ) -> None:
        native.setParent(None)  # type: ignore
