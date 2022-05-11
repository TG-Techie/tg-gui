from __future__ import annotations

from typing import TYPE_CHECKING, Protocol, TypeVar

if TYPE_CHECKING:
    from typing import Callable, ClassVar, Any, overload, Literal
    from typing_extensions import Self

    from ..tg_gui_core.widget import Widget

# ---

from tg_gui_core import implementation_support as impl_support
from tg_gui_core.shared import Identifiable

_T = TypeVar("_T")


class ProxyProvider(Protocol[_T]):

    if TYPE_CHECKING:

        def subscribe(
            self,
            *,
            subscriber: Identifiable,
            onupdate: Callable[[_T], None],
        ) -> Proxy[_T]:
            ...

        def unsubscribe(self, *, subscriber: Identifiable) -> None:
            ...


@impl_support.generic_compat
class Proxy(Protocol[_T]):
    if TYPE_CHECKING:

        def value(self, *, reader: Identifiable) -> _T:
            ...

        def update(self, value: _T, *, writer: Identifiable) -> None:
            ...
