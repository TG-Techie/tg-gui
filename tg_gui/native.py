from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

# circuilar imports
if TYPE_CHECKING:
    from typing import Callable, ClassVar, Any
    from .platform.shared import NativeElement, NativeContainer


_T = TypeVar("_T")
_NE = TypeVar("_NE", bound="NativeElement")
# ---

from abc import ABC, abstractmethod

# ---

from tg_gui_core import (
    Pixels,
    Widget,
    WidgetAttr,
    implementation_support as impl_support,
)

# ---

from .theming import ThemedAttr

# ---


@impl_support.generic_compat
class NativeWidget(Widget, Generic[_NE], ABC):
    native: _NE = WidgetAttr(init=False)

    def build(self, suggestion: tuple[Pixels, Pixels]) -> None:
        # see super()._build_ for docs
        super().build(suggestion)
        self.onupdate_theme(None)

    @abstractmethod
    def onupdate_theme(self, attr: ThemedAttr[Any] | None) -> None:
        """
        Called when an attribute of the theme changes,
        :param attr: The theme attribute object that provides the new value.
        """
        raise NotImplementedError
