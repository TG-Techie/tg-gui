from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import ClassVar, Type, Iterable, Any

# ---

from abc import ABC, abstractmethod, abstractproperty


class PlatformBackend(ABC):
    @abstractproperty
    def name(self) -> str:
        raise NotImplementedError
