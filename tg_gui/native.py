from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from typing import Callable, ClassVar
    from typing_extensions import Self
# ---

from abc import ABC, abstractmethod

# ---
from tg_gui_core.widget import Widget
from tg_gui_core import Pixels

# ---

from .theming import ThemedAttr

# ---

_T = TypeVar("_T")


class NativeWidget(Widget, ABC):
    def _build_(self, suggestion: tuple[Pixels, Pixels]) -> None:
        return super()._build_(suggestion)

    @abstractmethod
    def ontheme_update(self, attr: ThemedAttr[_T], value: _T) -> None:
        ...
