from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from typing import Callable, ClassVar
    from typing_extensions import Self

    ViewSyntax = Callable[["_SomeView"], "_W"]

else:
    ViewSyntax = object()

# ---
from tg_gui_core import (
    ContainerWidget,
    Widget,
    implementation_support as impl_support,
)

_SomeView = TypeVar("_SomeView", bound="View")
_W = TypeVar("_W", bound="Widget")


@impl_support.generic_compat
class View(ContainerWidget, Generic[_W]):

    body: ClassVar[ViewSyntax[Self]]
