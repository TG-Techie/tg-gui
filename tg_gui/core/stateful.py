from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Generic, Callable, Protocol, Any, overload

from ._shared import Identifiable, UID


_T = TypeVar("_T")
_C = TypeVar("_C")
_W = TypeVar("_W", bound="Widget")

if TYPE_CHECKING:
    from typing import Type
    from .widget import Widget

    _T_cn = TypeVar("_T_cn", contravariant=True)

    class _UpdateCallback(Protocol[_T_cn]):
        def __call__(self, value: _T_cn) -> None:
            ...


# class State(Generic[_T]):

#     def bound(self, *, relative_to: Widget) -> _T:
#         return self._wrapped

#     def __init__(self, wrapped: _T) -> None:
#         self._wrapped: _T = wrapped

#         self._subscribed: dict[UID, _UpdateCallback[_T]] = {}

#     @overload
#     def __get__(self, owner: None, ownertype: Type[_W]) -> State:
#         ...

#     @overload
#     def __get__(self, owner: _W, ownertype: Type[_W]) -> _T:
#         ...

#     def __get__(self, owner, ownertype):
#         if owner is None:
#             return self
#         else:
#             return self._wrapped

#     def __set__(self, owner: Widget, value: _T) -> None:
#         self.update(value, updater=owner)

#     @property
#     def wrapped(self) -> _T:
#         return self._wrapped

#     def update(self, value: _T, *, updater: Identifiable | None) -> None:
#         assert (
#             updater is None or updater._id_ in self._subscribed
#         ), f"{updater} is not subscribed to {self}"

#         if value != self._wrapped:
#             self._wrapped = value
#             self._update_subscribed(value, excluding=getattr(updater, "_id_", None))

#     def subscribe(
#         self,
#         subscriber: Identifiable,
#         callback: _UpdateCallback[_T],
#     ) -> None:
#         assert (
#             subscriber._id_ not in self._subscribed
#         ), f"{subscriber} is already subscribed to {self}"
#         self._subscribed[subscriber._id_] = callback

#     def unsubscribe(self, subscriber: Identifiable) -> None:
#         assert (
#             subscriber._id_ in self._subscribed
#         ), f"{subscriber} is not subscribed to {self}"
#         self._subscribed.pop(subscriber._id_)

#     def _update_subscribed(self, value: _T, *, excluding: UID | None) -> None:
#         for subid, update in self._subscribed.items():
#             if subid != excluding:
#                 update(value)

#     def __bool__(self) -> bool:
#         raise TypeError(f"Cannot use a states as a boolean")
