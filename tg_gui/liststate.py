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

# !! This file is a work in porgess !!

from __future__ import annotations

from tg_gui_core import (
    Widget,
    State,
    uid,
    UID,
    isoncircuitpython,
    Bindable,
    Identifiable,
)

from typing import TYPE_CHECKING

if not isoncircuitpython():
    from typing import *
    from enum import Enum, auto

    Handler = Callable[..., None]

T = TypeVar("T")

# --- enums for event types and Iterator internal state ---
if TYPE_CHECKING or not isoncircuitpython():

    class ListChange(Enum):
        removed = auto()
        swapped = auto()
        reorderafter = auto()
        inserted = auto()

    class _LSIterMode(Enum):
        unconfiged = auto()
        factory = auto()
        iterator = auto()


else:

    _LSIterMode = ConstantGroup("_LSIterMode", ("unconfiged", "factory", "iterator"))

    ListChange = ConstantGroup(
        "ListChange", ("removed", "swapped", "reorderafter", "inserted")
    )


class ListState(State, Generic[T]):

    _sugar_stack: ClassVar[list[_ListStateIterator[T]]] = []

    def __init__(self, ls: list[T]) -> None:

        # sugar guard
        # an allowed syntax for making a ListState is `State([1, 2, 3])`
        # when this used .__init__ may be called more than once, to check against is
        # we guard against this being inited
        if hasattr(self, "_src"):
            return

        assert isinstance(ls, list)

        # state interface
        self._id_ = uid()

        self._src = ls
        self._registered: dict[UID, Handler] = {}

    def value(self, reader: UID | Identifiable) -> ListState[T]:
        return self

    def update(self, updater: UID | Identifiable, value: T) -> None:
        raise NotImplementedError()

    def _register_handler_(self, key: UID | Identifiable, handler: Handler) -> None:
        key_src = key
        key = key if isinstance(key, UID) else key._id_
        if key in self._registered:
            raise ValueError(f"{self} already has a handler registered for {key_src}")
        self._registered[key] = handler

    def _deregister_handler_(self, key: UID | Identifiable) -> None:
        key = key if isinstance(key, UID) else key._id_
        self._registered.pop(key, None)

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:{self._id_} [...]>"

    # --- ---

    # --- sugar and iter ---
    def __iter__(self) -> Iterator[T]:
        lsiter = _ListStateIterator(self, self._src)
        self._push_lsiter_sugar(lsiter)
        return lsiter

    @classmethod
    def _push_lsiter_sugar(cls, lsiter: _ListStateIterator[T]) -> None:
        cls._sugar_stack.append(lsiter)

    @classmethod
    def _pop_lsiter_sugar(cls, lsiter: _ListStateIterator[T]) -> None:
        assert len(cls._sugar_stack), len(cls._sugar_stack)
        assert cls._sugar_stack[-1] is lsiter
        cls._sugar_stack.pop(-1)

    @classmethod
    def get_last_lsiter_sugar(cls: Type[ListState]) -> _ListStateIterator[T]:
        assert len(cls._sugar_stack)
        return cls._sugar_stack[-1]

    @classmethod
    def _get_sugar_stack(cls):
        return cls._sugar_stack


class _ListStateIterator(Generic[T]):
    def __init__(self, liststate: ListState[T], raw_list: list[T]) -> None:
        self._lsstate: None | ListState[T] = liststate
        self._raw_list: None | list[T] = raw_list

        self._mode = _LSIterMode.unconfiged
        self._ls_iter: None | Iterator[T] = None
        self._generator: None | Generator[Widget, None, None] = None
        self._factory_queue: None | list[T] = None

    def __iter__(self):
        return self

    def __next__(self):
        if self._mode is _LSIterMode.unconfiged:
            self._configure_as_iter_()

        if self._mode is _LSIterMode.factory:
            assert len(self._factory_queue)
            return self._factory_queue.pop(0)
        elif self._mode is _LSIterMode.iterator:
            assert self._ls_iter is not None
            try:
                return next(self._ls_iter)
            except StopIteration as err:
                self.__dict__.clear()
                raise err
        else:
            assert False, "unreachable"

    def _configure_as_iter_(self):
        assert (
            self._mode is _LSIterMode.unconfiged
        ), f"cannot re-configure, is already configured as {self._mode}"
        assert self._raw_list is not None

        self._mode = _LSIterMode.iterator

        # setup internal state
        self._ls_iter = iter(self._raw_list)

        # clear dependencies
        self._raw_list = None
        self._lsstate._pop_lsiter_sugar(self)

    def _configure_as_factory_(
        self, gen: Generator[Widget, None, None]
    ) -> ListState[T]:
        assert (
            self._mode is _LSIterMode.unconfiged
        ), f"cannot re-configure, is already configured as {self._mode}"
        assert self._lsstate is not None

        self._mode = _LSIterMode.factory

        # setup the internal state
        self._generator = gen
        self._factory_queue = []

        # remove from suagr stack
        self._lsstate._pop_lsiter_sugar(self)

        # clear dependencies
        lsstate = self._lsstate
        self._raw_list = None

        return lsstate

    def _process_model_(self, model: T) -> Widget:
        assert (
            self._mode is _LSIterMode.factory
        ), f"{self} is configures as {self._mode}, cannot be used for model processing"
        assert self._factory_queue is not None
        assert self._generator is not None

        self._factory_queue.append(model)
        return next(self._generator)

    def __call__(self, model: T) -> Widget:
        return self._process_model_(model)
