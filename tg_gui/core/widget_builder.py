from __future__ import annotations

from typing import TYPE_CHECKING, ClassVar, Type, TypeVar, Generic, Callable

from .widget import Widget, SuperiorWidget, PlatformWidget

class WidgetBuilder:

    def __init__(self, fn: Callable[[SuperiorWidget], Widget]: Type[SuperiorWidget],) -> None:
        pass

    def __get__(self, owner: SuperiorWidget | None, ownertype: Type[SuperiorWidget]) -> Widget:
        # circuitpython compatibility
        if owner is None:
            return self
        
        assert isinstance(owner, self._cls)