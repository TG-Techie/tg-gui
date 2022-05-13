from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, Protocol

if TYPE_CHECKING:
    from typing import Callable, ClassVar, Any
    from typing_extensions import Self
# ---

from abc import ABC, abstractmethod

from tg_gui_core._lib_env import *


WidgetType = TypeVar("WidgetType", bound=Widget)
SomeSelf = TypeVar("SomeSelf", bound="View", contravariant=True)


@widget
class View(ContainerWidget, Generic[WidgetType], ABC):
    class Syntax(Protocol[SomeSelf]):
        @staticmethod
        def __call__(self: SomeSelf) -> Any | WidgetType:
            ...

    body: ClassVar[Syntax[Self]]
