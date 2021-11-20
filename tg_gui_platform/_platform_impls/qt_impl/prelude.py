from tg_gui_core import Widget, Root, isoncircuitpython
from .screen import Screen


try:
    from typing import Callable
    from ...styling import Theme
except:
    pass


def default_screen() -> Screen:
    return Screen()


def _generate_default_size_from_screen(screen: Screen) -> tuple[int, int]:
    return (768, 480)
