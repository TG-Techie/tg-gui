from __future__ import annotations

from tg_gui_core import *

from typing import TYPE_CHECKING

from .shared import Color

from .stateful import State, StatefulAttr
from .theming import ThemedAttr

from .native import NativeWidget


# re-type @widget to include StatefulAttr, ThemedAttr, etc
if TYPE_CHECKING:
    from typing import TypeVar, Type, overload, Callable, Any
    from typing_extensions import dataclass_transform

    _W = TypeVar("_W", bound=Widget)

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

    _T = TypeVar("_T")
    _W = TypeVar("_W", bound=Widget)

    _Of = _T | State[_T] | StatefulAttr[_T]
    _Do = Callable[[_W, _T], None]

    @overload
    def onupdate(
        of: _Of[_T],
    ) -> Callable[[_Do[_W, _T]], _Do[_W, _T]]:
        ...

    @overload
    def onupdate(of: _Of[_T], do: _Do[_W, _T]) -> _Do[_W, _T]:
        ...


def onupdate(of: _Of[_T], do: _Do[_W, _T] | None = None) -> Any:
    assert isinstance(of, (StatefulAttr,)), (
        f"`of` must be a StatefulAttr, ThemedAttr, etc not `{of}`. the `_T | Proxy[_T]` type is "
        "used for typing compatibility, please do not actually use it."
    )
    attr: StatefulAttr[_T] = of
    if do is None:
        return attr.set_onupdate
    else:
        attr.set_onupdate(do)
        return do
