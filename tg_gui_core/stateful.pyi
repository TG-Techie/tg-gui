from typing import Tuple, TypeVar, Type, Callable, Any, Union, Generic, Protocol

from ._shared import uid, UID
from .base import Widget

T = TypeVar("T")

S = TypeVar("S")

class _Identifiable(Protocol):
    _id_: UID

Handler = Callable[[T], Any]

__all__ = (
    "State",
    "DerivedState",
)

class State(Generic[T]):
    def __init__(
        self,
        value: T,
        *,
        repr: Callable[[T], str] = repr,
    ) -> None: ...
    def value(self, reader: _Identifiable) -> T: ...
    def update(self, updater: _Identifiable, value: T) -> None: ...
    def __repr__(self) -> str: ...
    def __get__(self, owner: Widget, ownertype: Type[Widget]) -> T: ...
    def __set__(self, owner: Widget, value: T) -> None: ...
    def _register_handler_(
        self, key: None | _Identifiable, handler: Handler
    ) -> None: ...
    def _register_ha_deregister_handler_ndler_(
        self, key: None | _Identifiable
    ) -> None: ...
    def __rshift__(self, transform: Callable[[T], T]) -> DerivedState[T, T]: ...
    def __invert__(self) -> DerivedState[T, bool]: ...

class DerivedState(State, Generic[S, T]):
    def __init__(
        self,
        states: State[S] | Tuple[State[S], ...],
        fn: Callable[[S], T] | Callable[..., T],
    ) -> None: ...
