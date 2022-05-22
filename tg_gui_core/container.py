from __future__ import annotations

from tg_gui_core import annotation_only

if annotation_only():
    from typing import ClassVar, Type, Iterable, Any

# ---

from .widget import Widget

from abc import ABC, abstractmethod, abstractproperty


class ContainerWidget(Widget, ABC):
    @abstractproperty
    def children(self) -> Iterable[Widget]:
        raise NotImplementedError
