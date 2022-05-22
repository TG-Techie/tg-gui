from __future__ import annotations

from tg_gui_core import annotation_only

if annotation_only():
    from typing import ClassVar, Type, Iterable, Any

# ---

from abc import ABC, abstractmethod, abstractproperty


class PlatformBackend(ABC):
    @abstractproperty
    def name(self) -> str:
        raise NotImplementedError
