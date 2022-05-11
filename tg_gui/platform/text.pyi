from __future__ import annotations

from typing import TYPE_CHECKING

# circuilar imports
if TYPE_CHECKING:
    from typing import Any

# ---

from tg_gui_core import *

# ---
from .shared import NativeElement, NativeContainer
from .._platform_setup_ import *

# ---

@widget
class Text(NativeWidget):

    text: str = StatefulAttr(init=True, kw_only=False)
    @onupdate(text)
    def onupdate_text(self, text: str) -> None:
        raise NotImplementedError
    def onupdate_theme(self, attr: ThemedAttr[Any] | None) -> None:
        """
        called when a dependent themed attribute changes
        """
        raise NotImplementedError
    def _build_(
        self, suggestion: tuple[Pixels, Pixels]
    ) -> tuple[NativeElement, tuple[Pixels, Pixels]]:
        raise NotImplementedError
    def _demolish_(self, native: NativeElement) -> None:
        raise NotImplementedError
    def _place_(
        self,
        container: NativeContainer,
        native: NativeElement,
        pos: tuple[Pixels, Pixels],
        abs_pos: tuple[Pixels, Pixels],
    ) -> None:
        raise NotImplementedError
    def _pickup_(
        self,
        container: NativeContainer,
        native: NativeElement,
    ) -> None:
        raise NotImplementedError
