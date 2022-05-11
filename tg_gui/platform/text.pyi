from __future__ import annotations

from typing import TYPE_CHECKING

# circuilar imports
if TYPE_CHECKING:
    from tg_gui.text import Text
    from tg_gui.platform import NativeElement

from tg_gui_core._lib_env import Pixels

def build(
    self: Text, suggestion: tuple[Pixels, Pixels]
) -> tuple[NativeElement, tuple[Pixels, Pixels]]:
    """
    builds a native element that is the concrete implementation of the
    widget based on the suggested size.
    In this method, subclasses of Widget must:
    - assign self.native to the native element that corresponds to that subclass
    - assign self.dims based on the size of the native element
    """
    raise NotImplementedError

def update_style(self: Text) -> None:
    """
    called when a dependent themed attribute changes
    """
    raise NotImplementedError

def onupdate_text(self: Text, text: str) -> None:
    raise NotImplementedError
