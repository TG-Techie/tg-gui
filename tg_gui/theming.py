from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar

# ---
from tg_gui_core.attrs import WidgetAttr

# ---

# ---
_T = TypeVar("_T")


class ThemedAttr(WidgetAttr[_T]):
    pass
