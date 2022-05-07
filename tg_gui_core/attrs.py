from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from typing import TypeGuard, overload, Type, Any
    from typing_extensions import Self
    from .widget import Widget

    _W = Widget

_A = TypeVar("_A")
# ---

from abc import ABC, abstractmethod

from .shared import UID, Missing, MissingType
from .implementation_support import enum_compat, generic_compat


_W = TypeVar("_W", bound="Widget")


@generic_compat
class WidgetAttr(ABC, Generic[_A]):

    id: UID
    # flags in the subclass
    in_init: bool = False
    kw_only: bool
    in_build: bool
    in_style: bool
    # set by the base protocol
    name: str
    owning_cls: type
    private_name: str

    @abstractmethod
    def __init__(self) -> None:
        self.id = UID()

    @abstractmethod
    def init(self, widget: _W, value: _A | MissingType) -> None:
        pass

    @abstractmethod
    def get(self, widget: _W) -> _A | MissingType:
        raise NotImplementedError

    def set(self, widget: _W, value: _A | MissingType = Missing) -> None:
        raise AttributeError(
            f"{self.name} is a read-only attribute, tried to set to {value} on {widget}"
        )
        return None

    if TYPE_CHECKING:

        @overload
        def __get__(self, widget: None, ownertype: Type[_W]) -> Self:
            ...

        @overload
        def __get__(self, widget: _W, ownertype: Type[_W]) -> _A:
            ...

    def __get__(self, widget: _W | None, ownertype: Type[_W]) -> _A | Self:
        if widget is None:
            return self

        value = self.get(widget)

        if value is Missing:
            raise AttributeError(f"{self.name} cleared or not set, cannot be accessed")

        return value

    def __set__(self, widget: _W, value: _A | MissingType = Missing) -> None:
        return self.set(widget, value)

    def __set_name__(self, cls: Widget, name: str) -> None:
        assert (
            getattr(self, "name", None) is not None
        ), f"{self} already set, cannot set again to {name}"
        assert getattr(self, "owning_cls", None) is None

        assert name.startswith("_") == name.endswith(
            "_"
        ), f"invalid {type(self).__name__} name {name}, cannot be private (ie if it starts with _ it must end with _)"

        self.name = name
        self.owning_cls = cls
        if not getattr(self, "private_name", None):
            self.private_name = f"_{name if __debug__ else self.id}"

        assert (
            name != self.private_name
        ), f"{name} is the same as the private name in __set_name__"


# @generic
class ReservedAttr(WidgetAttr[_A]):

    required = False

    def __init__(
        self,
        *,
        build: bool = False,
        style: bool = False,
    ) -> None:
        super().__init__()
        self.in_build = build
        self.in_style = style

    def init(self, widget, value: MissingType) -> None:
        if value is not Missing:
            raise TypeError(
                f"{widget.__class__.__name__}.{self.name} is a reserved attribute, cannot be set in init"
            )
        setattr(widget, self.private_name, Missing)

    def get(self, owner: _W) -> _A:
        attr = getattr(self, self.private_name, Missing)
        if attr is Missing:
            raise AttributeError(
                f"{self} has not attribute `.{self.name}`, either uninited or cleared"
            )
        else:
            return attr

    def set(self, widget, value) -> None:
        return setattr(widget, self.private_name, value)
