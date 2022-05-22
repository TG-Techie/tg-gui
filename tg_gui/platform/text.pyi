from __future__ import annotations

from tg_gui_core import annotation_only

# circuilar imports
if annotation_only():
    from typing import Any

# ---

from tg_gui_core import *

# ---
from .shared import NativeElement, NativeContainer
from .._platform_setup_ import *

# ---

_NativeTextElement = NativeElement

@widget
class Text(NativeWidget[_NativeTextElement]):

    text: str = StatefulAttr(init=True, kw_only=False)

    # --- class specific side implementation methods ---
    @onupdate(text)
    def onupdate_text(self, text: str) -> None:
        raise NotImplementedError
    def onupdate_theme(self, attr: ThemedAttr[Any] | None) -> None:
        """
        called when a dependent themed attribute changes
        """
        raise NotImplementedError
    # --- abstract implementation methods ---
    def _build_(
        self, suggestion: tuple[Pixels, Pixels], *, text: str | State[str]
    ) -> tuple[NativeElement, tuple[Pixels, Pixels]]: ...
    def _demolish_(self, native: NativeElement) -> None: ...
    def _place_(
        self,
        container: NativeContainer,
        native: NativeElement,
        pos: tuple[Pixels, Pixels],
        abs_pos: tuple[Pixels, Pixels],
    ) -> None: ...
    def _pickup_(
        self,
        container: NativeContainer,
        native: NativeElement,
    ) -> None: ...
