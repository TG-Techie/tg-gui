from tg_gui_core import Widget
from ...styling import Theme, align

from .screen import Screen

from typing import Callable

def default_screen(*_) -> Screen:
    """
    An pre-written function to make a screen for quick TG-Gui setup
    takes no positional args
    """
    ...

def _generate_default_size_from_screen(screen: Screen) -> tuple[int, int]: ...
