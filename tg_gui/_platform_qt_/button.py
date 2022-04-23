from __future__ import annotations

from tg_gui._platform_support_ import platformmethod, platformimports
from typing import TYPE_CHECKING

# circular and annotation-only imports
if TYPE_CHECKING:
    from tg_gui.button import Button
    from typing import Callable

with platformimports():
    from tg_gui.core import Pixels
    from tg_gui.styling import Color

    from PySide6 import QtWidgets
    from PySide6.QtWidgets import QPushButton

    NativeElement = QPushButton


@platformmethod
def _build_native_(
    self: Button,
    suggestion: tuple[Pixels, Pixels],
    *,
    text: str,
    action: Callable[[], None],
) -> tuple[NativeElement, tuple[Pixels, Pixels],]:
    """
    Build the native button widget, set the text and connect the click event.
    """
    button = QPushButton(text)
    button.clicked.connect(action)
    button.show()
    suggested = button.size().toTuple()
    button.hide()
    print("_build_native_", self, suggested)
    return button, suggested


@platformmethod
def _native_style_(
    self: Button,
    *,
    radius: float,
    fill: Color,
    foreground: Color,
    active_fill: Color,
    active_foreground: Color,
) -> tuple[NativeElement, tuple[Pixels, Pixels],]:

    raise NotImplementedError
