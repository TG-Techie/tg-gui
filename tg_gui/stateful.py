from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar, Protocol
from tg_gui_core import *
from tg_gui_core.shared import Missing, MissingType, as_any


if TYPE_CHECKING:
    from typing import (
        Callable,
        ClassVar,
        Any,
        overload,
        Literal,
        Type,
        TypeGuard,
        TypeAlias,
    )
    from typing_extensions import Self

    _C = TypeVar("_C", bound="Callable")

    _OnupdateCallback = Callable[["_T"], None]
    _OnupdateMthd = Callable[[Widget, "_T"], None]

    Stateful: TypeAlias = "State[_T] | _T"

# ---

_T = TypeVar("_T")
_Widget = Widget


class ProxyProvider(Protocol[_T]):
    def get_proxy(self, owner: Widget) -> Proxy[_T]:
        ...


class Proxy(Protocol[_T]):
    def value(self, *, reader: Identifiable) -> _T:
        ...

    def update(self, value: _T, *, writer: Identifiable) -> None:
        ...

    def subscribe(
        self,
        *,
        subscriber: Identifiable,
        onupdate: Callable[[_T], None],
    ) -> Proxy[_T]:
        ...

    def unsubscribe(self, *, subscriber: Identifiable) -> bool:
        ...


def isstate(__obj: State[_T] | _T) -> TypeGuard[State[_T]]:
    return isinstance(__obj, State)


class State(Generic[_T]):
    """
    These wrap a value to update widgets as the value changes.
    State objects are usually auto-generated by the stateful descriptor but can be used as their own descriptors.
    """

    _value: _T
    _subscribed: dict[UID, _OnupdateCallback[_T]]

    def get_proxy(self, owner: Widget) -> Proxy[_T]:
        return self

    def value(self, *, reader: Identifiable) -> _T:
        return self._value

    def update(self, value: _T, *, writer: Identifiable) -> None:
        if value == self._value:
            return

        self._value = value

        #
        for uid, onupdate in self._subscribed.items():
            if uid == writer.id:
                continue
            onupdate(value)

    def subscribe(
        self,
        *,
        subscriber: Identifiable,
        onupdate: _OnupdateCallback[_T],
    ) -> Self:
        if subscriber.id in self._subscribed:
            raise ValueError(f"{subscriber} is already subscribed to {self}")

        self._subscribed[subscriber.id] = onupdate

        return self

    def unsubscribe(self, *, subscriber: Identifiable) -> bool:
        return self._subscribed.pop(subscriber.id, None) is not None

    if TYPE_CHECKING:

        @overload
        def __get__(self, instance: _Widget, owner: Type[_Widget]) -> _T:
            ...

        @overload
        def __get__(self, instance: None, owner: Type[_Widget]) -> Self:
            ...

    def __get__(self, instance, owner):
        if instance is None:
            return self
        else:
            return self.value(reader=instance)

    def __set__(self, instance: _Widget, value: _T) -> None:
        self.update(value, writer=instance)

    def __bool__(self) -> bool:
        raise TypeError("Cannot use a state as a boolean")

    if TYPE_CHECKING:

        def __new__(cls: type[Self], value: _T) -> _T:
            ...

    else:

        def __init__(self, value: _T) -> None:
            # TODO: allow write locking based on id
            self._value = value
            self._subscribed: dict[UID, _OnupdateCallback[_T]] = {}


_T = TypeVar("_T")


class StatefulAttr(WidgetAttr[_T]):

    _onupdate: _OnupdateMthd[_T] | None

    # TODO: add get_attr, set_attr, and init_attr methods

    def init_attr(self, owner: _Widget, value: _T | State[_T] | MissingType) -> None:
        setattr(owner, self.private_name, value)

        if value is not Missing and isstate(value):
            self._subscribe_to_state(owner, value)

    def del_attr(self, owner: _Widget) -> None:
        # unsubscribe from the old state if it is a state
        existing = self.get_raw_attr(owner)
        if isstate(existing):
            existing.unsubscribe(subscriber=owner)

    def get_raw_attr(self, widget: _Widget) -> _T | State[_T]:
        """
        returns the unsugared instance attribute value. This may be a raw value or a State instance that wraps that value.
        """
        return getattr(widget, self.private_name)

    def get_attr(self, owner: _Widget) -> _T:
        attr: _T | State[_T] = self.get_raw_attr(owner)

        if isstate(attr):
            value = attr.value(reader=owner)
        else:
            assert not isinstance(attr, State)
            value = attr

        return value

    def get_proxy(self, owner: _Widget) -> State[_T]:
        existing = self.get_raw_attr(owner)

        if isstate(existing):
            return existing
        else:
            assert not isinstance(existing, State)
            # auto-generate a state, set it and re-turn it
            value: State[_T] = as_any(State(existing))
            self._subscribe_to_state(owner, value)
            setattr(owner, self.private_name, value)
            return value

    def set_onupdate(self, onupdate: _OnupdateMthd[_T]) -> _OnupdateMthd[_T]:
        # make sure one is not already set
        if self._onupdate is not None:
            raise ValueError(f"onupdate is already proided for {self}.")
        else:
            # TODO: fix this?
            self._onupdate = onupdate
        return onupdate

    def _subscribe_to_state(self, owner: _Widget, state: State[_T]) -> None:
        if self._onupdate is not None:
            state.subscribe(
                subscriber=owner,
                onupdate=getattr(owner, self._onupdate.__name__),
            )

    # NOTE: this uses pep 681, which is to be approved
    if TYPE_CHECKING:
        # NOTE: this uses pep 681 that is yet to be approved.
        # see tg_gui_core.attrs.py for what this is overriding.

        @overload
        def __new__(
            cls,
            default: State[_T] | _T,
            onupdate: _OnupdateCallback | None = None,
            *,
            init: Literal[True] = True,
        ) -> Any:
            ...

        @overload
        def __new__(
            cls,
            *,
            factory: Callable[[], _T],
            onupdate: _OnupdateCallback | None = None,
            init: Literal[True] = True,
        ) -> Any:
            ...

        @overload
        def __new__(
            cls,
            *,
            init: Literal[True] = True,
            onupdate: _OnupdateCallback | None = None,
            kw_only: bool = True,
        ) -> Any:
            ...

        def __new__(cls, *_, **__) -> Any:
            ...

    else:

        pass
        # see below for the init implementation

    def __widattr_init__(
        self: StatefulAttr[_T],
        default: _T | State[_T] | MissingType = Missing,
        # onupdate: _OnupdateCallback[_T] | None = None,
        *,
        factory: Callable[[], _T] | MissingType = Missing,
        init: Literal[True] = True,
        kw_only: bool | MissingType = Missing,
    ) -> None:
        assert init is True, "init must be True"

        if default is not Missing:
            assert (
                factory is Missing
            ), f"{self.__class__.__name__}(...) got arguments for 'default' and 'factory', only one is allowed."
            assert (
                kw_only is Missing
            ), f"{self.__class__.__name__}(...) got arguments for 'default' and 'kw_only', only one is allowed."
            super(StatefulAttr, self).__widattr_init__(default=default, init=True)  # type: ignore
        elif factory is not Missing:
            assert (
                kw_only is Missing
            ), f"{self.__class__.__name__}(...) got arguments for 'factory' and 'kw_only', only one is allowed."
            super(StatefulAttr, self).__widattr_init__(default_factory=factory, init=True)  # type: ignore
        else:
            super(StatefulAttr, self).__widattr_init__(init=True, kw_only=kw_only or True)  # type: ignore

        self._onupdate = None
