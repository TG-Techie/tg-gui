from __future__ import annotations

from tg_gui_core import *

from typing import TYPE_CHECKING, TypeVar

from .shared import Color

from .stateful import State, StatefulAttr
from .theming import ThemedAttr

from .native import NativeWidget


# re-type @widget to include StatefulAttr, ThemedAttr, etc
if TYPE_CHECKING:
    from typing import TypeVar, Type, overload, Callable, Any
    from typing_extensions import dataclass_transform

    _W = TypeVar("_W", bound=Widget)
    _T = TypeVar("_T")


if TYPE_CHECKING:

    @dataclass_transform(
        eq_default=False,
        order_default=False,
        kw_only_default=True,
        field_descriptors=(
            WidgetAttr,
            StatefulAttr,
            ThemedAttr,
        ),
    )
    def widget(cls: Type[_W]) -> Type[_W]:
        ...

else:
    from tg_gui_core.attrs import widget


if TYPE_CHECKING:

    _Of = _T | State[_T] | StatefulAttr[_T]
    _Do = Callable[[_W, _T], None]

    @overload
    def onupdate(of: _Of[_T], do: None = None) -> Callable[[_Do[_W, _T]], _Do[_W, _T]]:
        ...

    @overload
    def onupdate(of: _Of[_T], do: _Do[_W, _T]) -> _Do[_W, _T]:
        ...


def onupdate(of: _Of[_T], do: _Do[_W, _T] | None = None) -> Any:

    # while this is typed to accept _T | State | StatefulAttr it actiually only accepts
    # StatefulAttr[_T]

    # you cannot use isinstance with a StatefulAttr[_T] at runtime,
    # so assert without it at runtime
    if TYPE_CHECKING and not isinstance(of, (StatefulAttr[_T])):
        raise TypeError
    else:
        assert isinstance(of, (StatefulAttr)), (
            f"`of` must be a StatefulAttr, ThemedAttr, etc not `{of}`. the "
            "`_T | Proxy[_T]` type is used for typing compatibility, "
            "please do not actually use it."
        )

    if do is None:
        return of.set_onupdate
    else:
        # This passes a _W TypeVar to a flat Widget type and makes pyrihgt unhappy
        return of.set_onupdate(do)  # pyright: reportGeneralTypeIssues=false
