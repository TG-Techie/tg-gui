from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from typing import (
        Callable,
        ClassVar,
        Any,
        overload,
        Literal,
        Union,
    )
    from typing_extensions import Self

    _C = TypeVar("_C", bound="Callable")

    _OnupdateCallback = Callable[["_T"], None]
    _OnupdateMthd = Callable[["_W", "_T"], None]
# ---

from tg_gui_core._lib_env import *
from .proxying import ProxyProvider, Proxy

_T = TypeVar("_T")
_W = TypeVar("_W", bound=Widget)


class State(Proxy[_T], ProxyProvider[_T]):
    def __init__(self, value: _T) -> None:
        super().__init__()
        self._value = value
        self._subscribed: dict[UID, _OnupdateCallback[_T]] = {}

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
        onupdate: _OnupdateCallback,
    ) -> Self:
        if subscriber.id in self._subscribed:
            raise ValueError(f"{subscriber} is already subscribed to {self}")

        self._subscribed[subscriber.id] = onupdate

        return self

    def unsubscribe(self, *, subscriber: Identifiable) -> None:
        return super().unsubscribe(subscriber=subscriber)


class StatefulAttr(WidgetAttr[_T]):

    _onupdate: _OnupdateCallback[_T] | None

    def set_onupdate(self, onupdate: _OnupdateMthd[_W, _T]) -> _OnupdateMthd[_W, _T]:
        # make sure one is not already set
        if self._onupdate is not None:
            raise ValueError(f"onupdate is already proided for {self}.")
        else:
            # TODO: fix this?
            self._onupdate = onupdate
        return onupdate

    # NOTE: this uses pep 681, which is to be approved
    if TYPE_CHECKING:
        # NOTE: this uses pep 681 that is yet to be approved.
        # see tg_gui_core.attrs.py for what this is overriding.
        @overload
        def __new__(
            cls,
            default: _T,
            onupdate: _OnupdateCallback | None = None,
            *,
            init: Literal[True] = True,
        ) -> _T:
            ...

        @overload
        def __new__(
            cls,
            *,
            factory: Callable[[], _T],
            onupdate: _OnupdateCallback | None = None,
            init: Literal[True] = True,
        ) -> _T:
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
        default: _T | MissingType = Missing,
        onupdate: _OnupdateCallback[_T] | None = None,
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

        self._onupdate = onupdate
