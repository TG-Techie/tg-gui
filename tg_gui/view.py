from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from typing import Callable, ClassVar
    from typing_extensions import Self

    ViewSyntax = Callable[["_SomeView"], "_W"]

else:
    ViewSyntax = object()

# ---

from abc import ABC, abstractmethod

from tg_gui_core._lib_env import *

_SomeView = TypeVar("_SomeView", bound="View", contravariant=True)
_W = TypeVar("_W", bound="Widget")


@widget
@impl_support.generic_compat
class View(ContainerWidget, ABC, Generic[_W, _SomeView]):

    body: Callable[[_SomeView], _W] = WidgetAttr(init=False)
