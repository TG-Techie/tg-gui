from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import ClassVar, Type, Iterable, Any

# ---

from .widget import Widget

from abc import ABC, abstractmethod, abstractproperty


class ContainerWidget(Widget, ABC):
    @abstractproperty
    def children(self) -> Iterable[Widget]:
        raise NotImplementedError
