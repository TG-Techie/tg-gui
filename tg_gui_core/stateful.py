# The MIT License (MIT)
#
# Copyright (c) 2021 Jonah Yolles-Murphy (TG-Techie)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import annotations

from ._shared import uid, UID, isoncircuitpython

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import *


T = TypeVar("T")
S = TypeVar("S")

if TYPE_CHECKING:
    # Handler = Callable[[T], Any]
    Handler = Callable[..., Any]
    # DerivedHandler = Callable[..., Any]

    class Identifiable(Protocol):
        _id_: UID

    B = TypeVar("B", bound=Hashable)

    class Bindable(Protocol[B]):
        def value(self, reader: UID | Identifiable) -> B:
            ...

        def update(self, updater: UID | Identifiable, value: B) -> None:
            ...

        def _register_handler_(self, key: UID | Identifiable, handler: Handler) -> None:
            ...

        def _deregister_handler_(self, key: UID | Identifiable) -> None:
            ...


else:
    from ._shared import _BracketByPass as Bindable

    Identifiable = object


def _not(obj: object) -> bool:
    return not obj


class State(Bindable[T]):
    def __init__(self, value: T, *, repr: Callable[[T], str] = repr) -> None:
        self._id_ = uid()
        self._value = value

        self._registered: dict[UID, Handler] = {}
        self._single_upate_handlers: list[Handler] = []

        self._repr = repr

    def update(self, updater, value: T) -> None:
        if value != self._value:
            self._value = value
            self._alert_registered(updater)

    def value(self, reader) -> T:
        return self._value

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:{self._id_} ({self._repr(self._value)})>"

    def __get__(self, owner, ownertype) -> T:
        """
        For using states as values in functions, great for button actions.
        """
        # # called with self as a `.some_state` doesn't care
        return self if owner is None else self.value(self)  # type: ignore

    def __set__(self, owner, value: T) -> None:
        """
        For using states as values in functions, great for button actions.
        """
        self.update(self, value)
        # called with self as an assignmetn should update everybody

    def _register_handler_(self, key, handler: Handler) -> None:
        if key is None:
            self._single_upate_handlers.append(handler)
        elif key not in self._registered:
            if hasattr(key, "_id_"):
                key = key._id_
            self._registered[key] = handler

        else:
            raise ValueError(f"{self} already has a handler registered for  {key}")

    def _deregister_handler_(self, key) -> None:
        registered = self._registered
        if hasattr(key, "_id_"):
            key = key._id_
        if key in registered:
            registered.pop(key)

    def _alert_registered(self, excluded):
        excluded_key = getattr(excluded, "_id_", excluded)

        value = self._value
        for handler in self._single_upate_handlers:
            handler(value)
            self._single_upate_handlers = []
        for key, handler in self._registered.items():
            if key is not excluded_key:
                handler(value)

    def __rshift__(self, transform: Callable[[T], T]) -> "DerivedState":
        """
        sugar to make derived states clearer to understand
        """
        return DerivedState(self, transform)

    def __bool__(self):
        raise TypeError(f"`{self}` cannot be cast to a bool, try `{self} >> bool`")

    def __invert__(self) -> "DerivedState":
        return DerivedState(self, _not)


class DerivedState(State, Generic[S, T]):
    def __init__(
        self,
        states: State[S] | tuple[State[S], ...],
        fn: Callable[[S], T] | Callable[..., T],
    ) -> None:
        if isinstance(states, State):
            states = (states,)
        elif isinstance(states, tuple):
            pass
        else:
            raise ValueError(f"argument states must be a State or tuple of States")

        self._src_states = states
        self._fn = fn

        super().__init__(value=self)

        self._register_with_sources()
        self._update_from_sources(None)

    def update(self, updater, value, **__):
        raise TypeError(f"you cannot set the state of {self}, tried to set to {value}")

    def __repr__(self):
        return f"<{type(self).__name__}:{self._id_} {self._src_states}>"

    def _update_from_sources(self, _):
        """
        a hander that recalcuates the derived state from the given source states
        and updates any handlers registered to this state
        """
        super().update(self, self._derive_new_state())

    def _derive_new_state(self):
        substates = [state.value(self) for state in self._src_states]
        return self._fn(*substates)

    def _register_with_sources(self):
        for state in self._src_states:
            state._register_handler_(self, self._update_from_sources)

    def _deregister_from_sources(self):
        for state in self._src_states:
            state._deregister_handler_(self)
