from __future__ import annotations

from .implementation_support import (
    isoncircuitpython,
    class_id as _class_id,
    GenericABC,
)

from ._shared import uid, UID


from typing import TYPE_CHECKING, TypeVar, Generic, overload

_W = TypeVar("_W", bound="Widget")
_T = TypeVar("_T")
_SomeWidgetAttr = TypeVar("_SomeWidgetAttr", bound="WidgetAttr")

if TYPE_CHECKING:
    from typing import Type
    from .widget import Widget


class WidgetAttr(GenericABC[_T]):

    # TODO: add _build_proxy_ method to either throw error, return value, or bind to state

    # --- public attributes ---
    _id_: UID
    _name_: str

    # --- abstract attributes ---
    _required_: bool
    _build_: bool

    # --- private concrete attributes ---
    _private_name: str
    _repr: bool
    _owning_cls: Type[Widget]

    def __init__(
        self,
        *,
        repr: bool = False,
        private_name: str | None = None,
    ) -> None:
        self._id_ = uid()

        self._repr = repr

        # set in __set_name__
        self._name_ = None  # type: ignore[assignment]
        self._owning_cls = None  # type: ignore[assignment]
        self._private_name = private_name  # type: ignore[assignment]

    def __repr__(self) -> str:
        if self._name_ is None:
            return f"<{self.__class__.__name__}: {self._id_}>"
        else:
            return (
                f"<{type(self).__name__} "
                + f"{self._owning_cls.__module__}.{self._owning_cls.__name__}.{self._name_}>"
            )

    def __set_name__(self, cls: Type[Widget], name: str) -> None:
        assert self._name_ is None, f"{self} already set, cannot set again to {name}"
        assert self._owning_cls is None
        assert name.startswith("_") == name.endswith(
            "_"
        ), f"invalid {type(self).__name__} name {name}, cannot be private (ie if it starts with _ it must end with _)"

        self._name_ = name
        self._owning_cls = cls
        if not self._private_name:
            self._private_name = f"_{name if __debug__ else ''}_{self._id_}"

        assert (
            name != self._private_name
        ), f"{name} is the same as the private name in __set_name__"

    @overload
    def __get__(
        self: _SomeWidgetAttr, owner: None, ownertype: Type[_W]
    ) -> _SomeWidgetAttr:
        ...

    @overload
    def __get__(self, owner: _W, ownertype: Type[_W]) -> _T:
        ...

    def __get__(self, owner: None | _W, ownertype: Type[_W]) -> _T | WidgetAttr[_T]:
        assert self._name_ is not None, f"{self} not initialized with __set_name__"
        # circuitpython-compat(__get__)
        if owner is None:
            return self  # type: ignore[return-value]
        return self.get(owner)

    def get(self, owner: Widget) -> _T:
        return getattr(owner, self._private_name)

    def set(self, owner: Widget, value: _T) -> None:
        setattr(owner, self._private_name, value)


# circuitpython-compat(__class_getitem__) not supported, so we have to do this
if not TYPE_CHECKING and isoncircuitpython():
    _InitAttr = WidgetAttr
    WidgetAttr = {_T: _InitAttr}


def buildattr(*, repr=False, private_name: str | None = None) -> BuildAttr:
    return BuildAttr(repr=repr, private_name=private_name)  # type: ignore


class BuildAttr(WidgetAttr[_T]):

    _required_: bool = True
    _build_: bool = True

    def get(self, owner: Widget) -> _T:
        return getattr(owner, self._private_name)

    def set(self, owner: Widget, value: _T) -> None:
        setattr(owner, self._private_name, value)


# circuitpython-compat(__class_getitem__) finish
if not TYPE_CHECKING and isoncircuitpython():
    WidgetAttr = _InitAttr
    del _InitAttr
