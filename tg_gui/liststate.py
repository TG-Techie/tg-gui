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
    enum_compat,
    Identifiable,
    Bindable,
    USE_TYPING,
)

from enum import Enum, auto

from typing import TYPE_CHECKING

if USE_TYPING:
    from typing import *

T = TypeVar("T")

# --- enums for event types and Iterator internal state ---


@enum_compat
class ListChange(Enum):
    pop = auto()  # index
    insert = auto()  # index
    refresh = auto()  # None
    changed = auto()  # index


@enum_compat
class _LSIterMode(Enum):
    unconfiged = auto()
    # generator state
    factory = auto()
    # iterating states
    iterating = auto()
    closed = auto()


if USE_TYPING:
    # Callable[[ListChange, Union[None, int, tuple[int, int]]], None]
    ChangePayload = Union[None, int, tuple[int, int]]
    Handler = Callable[[ListChange, ChangePayload], None]


def _liststate_and_factory_from_generator_(
    gen: Generator[Widget, None, None]
) -> tuple[ListState[T], ListStateIterator[T]]:
    lsiter: ListStateIterator[T]
    lsiter = ListStateIterator._get_last_created_()
    return lsiter._configure_as_factory_(gen), lsiter


class ListState(State, Generic[T], Bindable["ListState[T]"]):
    def __init__(self, ls: list[T]) -> None:

        # sugar guard
        # an allowed syntax for making a ListState is `State([1, 2, 3])`
        # when this used .__init__ may be called more than once, to check against is
        # we guard against this being inited
        if hasattr(self, "_source"):
            return

        assert isinstance(ls, list)

        # state interface
        self._id_ = uid()

        self._source = ls
        self._registered: dict[UID, Handler] = {}

    def __get__(self, owner, ownertype) -> T:
        return self

    def __set__(self, owner, value: T) -> None:
        """
        For using states as values in functions, great for button actions.
        """
        if value is self:
            raise NotImplementedError
            self._alert_on_change(ListChange.reorderafter, NOne)

        raise NotImplementedError

    def value(self, reader: UID | Identifiable) -> ListState[T]:
        return self

    def update(self, updater: UID | Identifiable, value: T) -> None:
        raise NotImplementedError("... working on it")

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

    def _alert_on_change(
        self,
        change: ListChange,
        payload: ChangePayload,
        excluded: UID | Identifiable,
    ):
        excluded = excluded if isinstance(excluded, UID) else Identifiable._id_

        for key, handler in self._registered.items():
            if key == excluded:
                continue
            handler(change, payload)

    # --- list interface and updates ---

    # append          clear           copy            count
    # extend          index           insert          pop
    # remove          reverse         sort

    def append(self, value: T) -> None:
        dest_index = len(self._source)
        self._source.append(value)
        self._alert_on_change(ListChange.insert, dest_index)

    def clear(self) -> None:
        self._source.clear()
        self._alert_on_change(ListChange.refresh)

    def count(self, value: T) -> int:
        return self._source.count(value)

    def extend(self, iterable: Iterable[T]) -> None:
        source = self._source
        initial = len(source)
        source.extend(iterable)
        # TODO: figure out how to make this only partial
        self._alert_on_change(ListChange.refresh, None)

    def index(self, value: T) -> int:
        return self._source.index(value)

    def insert(self, index: int, value: T) -> None:
        index = index % len(self._source)
        self._source.insert(index, value)
        self._alert_on_change(ListChange.insert, index)

    def pop(self, index: None | int = None) -> T:
        if index is None:
            raise ValueError(
                ".pop() missing argument 'index' "
                + "(if that's and issue ... please get over it)"
            )

        index = index % len(self._source)
        self._source.pop(index)
        self._alert_on_change(ListChange.pop, index)

    def remove(self, value: T) -> None:
        self.pop(self._source.index(value))

    def reverse(self) -> None:
        self._source.reverse()
        self._alert_on_change(ListChange.refresh, None)

    def sort(self, **kwargs) -> None:
        self._source.sort(**kwargs)
        self._alert_on_change(ListChange.refresh, None)

    def __setitem__(self, __idx: int, value: T) -> None:
        index = __idx % len(self._src)
        self._source[index] = value
        self._alert_on_change(ListChange.changed, index)

    def __getitem__(self, __idx_slc: int | slice) -> T:
        return self._source.__getitem__(__idx_slc)

    def __len__(self) -> int:
        return len(self._source)

    # --- iter, sugar, and extended functionality ---

    def __iter__(self) -> Iterator[T]:
        return ListStateIterator(self, self._source)

    def __reversed__(self) -> Iterator[T]:
        return ListStateIterator(self, self._source, reversed=True)

    def iter(self, reversed: bool = False) -> Iterator[T]:
        return reversed(self._source) if reversed else iter(self._source)


class ListStateIterator(Generic[T]):

    _sugar_stack: ClassVar[list[ListStateIterator[T]]] = []

    def __init__(
        self, liststate: ListState[T], raw_list: list[T], reversed: bool = False
    ) -> None:
        # shared state / resources
        self._id_ = _id_ = uid()
        self._reversed = reversed

        self._mode = _LSIterMode.unconfiged

        self._source_state = liststate
        self._raw_list = raw_list

        self._add_to_sugar()

        # _LSIterMode.iterator internal State (reserves memory)
        self._raw_iter: Iterator[T] = None  # type: ignore

        # _LSIterMode.factory internal State (reserves memory)
        self._gen: Generator[Widget, None, None] = None  # type: ignore
        self._gen_queue: list[T] = None  # type: ignore

    def isconfiged(self) -> bool:
        return self._mode is not _LSIterMode.unconfiged

    def isfactory(self) -> bool:
        return self._mode is _LSIterMode.factory

    def isiterating(self) -> bool:
        return self._mode is _LSIterMode.iterating

    def isclosed(self) -> bool:
        return self._mode is _LSIterMode.closed

    def __repr__(self) -> str:
        mode = self._mode
        title = f"{type(self).__name__}:{self._id_} "

        if mode is _LSIterMode.unconfiged:
            return f"<{title}>"
        elif mode in {
            _LSIterMode.iterating,
            _LSIterMode.closed,
        }:
            ls = f"[{type(self._source_state).__name__}:{self._source_state._id_}]"
            ls = f"reversed({ls})" if self._reversed else ls
            if mode is _LSIterMode.iterating:
                return f"<{title} over {ls}>"
            elif mode is _LSIterMode.closed:
                return f"<{title} closed iterator over {ls}>"
            else:
                assert False, "unreachable"
        elif mode is _LSIterMode.factory:
            return f"<{title} as factory>"
        else:
            assert False, "unreachable"

    def __iter__(self):
        return self

    def __next__(self):

        if self._mode is _LSIterMode.unconfiged:
            self._configure_as_iter_()

        mode = self._mode

        if mode is _LSIterMode.factory:
            if len(self._gen_queue) == 1:
                return self._gen_queue.pop(0)
            elif len(self._gen_queue) == 0:
                raise StopIteration(
                    f"cannot iterate over a liststate as a factory, tried to iter over {self}"
                )
            else:
                raise RuntimeError(f"internal list state error in {self}")

        elif mode is _LSIterMode.iterating:
            assert self._raw_iter is not None
            try:
                return next(self._raw_iter)
            except StopIteration:
                self._mode = _LSIterMode.closed
                raise StopIteration

        elif mode is _LSIterMode.closed:
            raise StopIteration

        else:
            assert False, f"unreachable, {mode}"

    def _configure_as_iter_(self) -> None:
        assert (
            self._mode is _LSIterMode.unconfiged
        ), f"cannot re-configure, is already configured as {self._mode}"

        self._mode = _LSIterMode.iterating
        self._assert_claim_sugar()
        # self._open_as_iterator()

        # setup the internal state
        # once an iterator over is it created a reference to the base list is not needed
        self._raw_iter = (
            reversed(self._raw_list) if self._reversed else iter(self._raw_list)
        )
        self._raw_list = None  # type: ignore

    def _configure_as_factory_(
        self, gen: Generator[Widget, None, None]
    ) -> ListState[T]:
        assert (
            self._mode is _LSIterMode.unconfiged
        ), f"cannot re-configure, is already configured as {self._mode}"
        assert self._source_state is not None

        if not self._reversed:
            # TODO: should iterators close on errors?
            # self._mode = _LSIterMode.closed
            raise SyntaxError(
                "Cannot use `reversed(...)` on a ListState in a generator context. "
                + "ie, cannot use List(... for a, b in reversed(<some_list_state>))"
            )

        # sugar and mode
        self._mode = _LSIterMode.factory
        self._assert_claim_sugar()
        # setup the internal state
        self._gen = gen
        self._gen_queue = []

        # clear dependency, references to these are not needed
        source = self._source_state
        self._raw_list = None  # type: ignore
        self._source_state = None  # type: ignore

        return source

    def _process_model_(self, model: T) -> Widget:
        assert (
            self._mode is _LSIterMode.factory
        ), f"{self} is configures as {self._mode}, cannot be used for model processing"

        self._gen_queue.append(model)
        return next(self._gen)

    if TYPE_CHECKING:

        def __call__(self, model: T) -> Widget:
            return self._process_model_(model)

    else:
        __call__ = _process_model_

    def _add_to_sugar(self) -> None:
        self._sugar_stack.append(self)

    def _assert_claim_sugar(self) -> None:
        assert len(
            self._sugar_stack
        ), f"[sugar error] ListStateIterator stack already empty"

        top = self._sugar_stack.pop(-1)

        assert top._id_ == self._id_, (
            "[sugar error] stack corrupted, "
            + f"expected {self} on top but found {top}"
        )

    @classmethod
    def _get_last_created_(cls) -> ListStateIterator:
        assert len(cls._sugar_stack), "no new ListStateIterators"
        return cls._sugar_stack[-1]

    def __del__(self):
        if self._mode is _LSIterMode.iterating:
            self._close_as_iterator()
