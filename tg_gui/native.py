from __future__ import annotations

from typing import Generic, TypeVar
from tg_gui_core import annotation_only

# circuilar imports
if annotation_only():
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
    widget,
    implementation_support as impl_support,
)

# ---

from .stateful import State, StatefulAttr
from .theming import ThemedAttr

# ---


@widget
class NativeWidget(Widget, ABC, Generic[_NE]):

    native: _NE = WidgetAttr(init=False)

    def build(self, suggestion: tuple[Pixels, Pixels]) -> None:
        # see super()._build_ for docs
        # dins the stateful attrs and pass it to the build method
        stateful_attr_values = {
            name: attr.get_raw_attr(self)
            for name, attr in self.__widget_attrs__.items()
            if isinstance(attr, StatefulAttr)
        }
        super().build(suggestion, **stateful_attr_values)
        self.onupdate_theme(None)

    @abstractmethod
    def onupdate_theme(self, attr: ThemedAttr[Any] | None) -> None:
        """
        Called when an attribute of the theme changes,
        :param attr: The theme attribute object that provides the new value.
        """
        raise NotImplementedError

    if annotation_only():

        @abstractmethod
        def _build_(
            self,
            suggestion: tuple[Pixels, Pixels],
            **kwargs: Any | State[Any],
        ) -> None:
            raise NotImplementedError

        @abstractmethod
        def _demolish_(self, native: _NE) -> None:
            raise NotImplementedError

        @abstractmethod
        def _place_(
            self,
            container: NativeContainer,
            native: _NE,
            pos: tuple[Pixels, Pixels],
            abs_pos: tuple[Pixels, Pixels],
        ) -> None:
            raise NotImplementedError

        @abstractmethod
        def _pickup_(
            self,
            container: NativeContainer,
            native: _NE,
        ) -> None:
            raise NotImplementedError
