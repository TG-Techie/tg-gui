from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, Protocol

if TYPE_CHECKING:
    from typing import Callable, ClassVar, Any
    from typing_extensions import Self

    _T = TypeVar("_T")
    _AnyButActually = Any | _T

# ---

from abc import ABC, abstractmethod

from tg_gui_core._lib_env import *


Wrapped = TypeVar("Wrapped", bound=Widget)
SomeSelf = TypeVar("SomeSelf", bound="View", contravariant=True)


@widget
class View(ContainerWidget, Generic[Wrapped], ABC):
    class Syntax(Protocol[SomeSelf]):
        @staticmethod
        def __call__(
            self: SomeSelf,  # pyright: reportSelfClsParameterName=false
        ) -> _AnyButActually[Wrapped]:
            ...

    body: ClassVar[Syntax[Self]]
