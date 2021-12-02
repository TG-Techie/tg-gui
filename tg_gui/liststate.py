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

if TYPE_CHECKING:
    changes = lambda *args: (lambda fn: fn)
else:

    def changes(*managers: ContextManager):
        def decorate(fn):
            if len(managers) == 0:

                def wrapped_fn(*args, __mngr: ContextManager = managers[0], **kwargs):
                    __mngr.__enter__()
                    try:
                        ret = fn(*args, **kwargs)
                    except Exception as expt:
                        __mngr.__exit__(type(expt), expt)
                        raise expt
                    else:
                        __mngr.__exit__(None, None)
                        return ret

            else:

                def wrapped_fn(
                    *args,
                    __changes_managers___: tuple[ContextManager] = managers,
                    **kwargs,
                ):
                    for mngr in __changes_managers___:
                        mngr.__enter__()

                    try:
                        ret = fn(*args, **kwargs)
                    except Exception as expt:
                        for mngr in __changes_managers___:
                            mngr.__exit__(type(expt), expt)
                        raise expt
                    else:
                        for mngr in __changes_managers___:
                            mngr.__exit__(None, None)
                        return ret

            return wrapped_fn

        return decorate


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
        if "_source" in self.__dict__:
            return

        assert isinstance(ls, list)

        # state interface
        self._id_ = uid()
        self._change_nesting: int = 0
        self._change_guard: set[Identifiable] = set()

        self._source: list[T] = ls
        # self._static_souce: None | tuple[T] = tuple(ls)
        self._registered: dict[UID, Handler] = {}

    def __get__(self, owner, ownertype) -> list[T] | ListState[T]:
        # print(f"{self}.__get__({owner}, {ownertype})")
        if owner is None:
            return self
        else:
            if self._change_nesting == 0:
                return self
                # return self._static_souce
                # raise RuntimeError(
                #     "list states cannot be mutated outside of a mutating context, "
                #     + "use `with <list state>: ...` or `@changes(<list state>)`"
                # )
            self._change_guard.add(self)
            return self._source

    def __set__(self, owner, value: T) -> None:
        """
        For using states as values in functions, great for button actions.
        """
        if value is self:
            raise NotImplementedError

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
        excluded: None | UID | Identifiable | Iterable[None | UID | Identifiable],
    ):
        if not isinstance(excluded, (tuple, list, set)):
            assert (
                excluded is None
                or isinstance(excluded, UID)
                or hasattr(excluded, "_id_")
            ), (
                "exlcuded= must be a (None, UID, Identifiable) or a "
                + f"(list, tuple, or set) of those, found {excluded}"
            )
            excluded = (excluded,)

        excluded: set[UID] = set(
            (ext if ext is None or isinstance(ext, UID) else ext._id_)
            for ext in excluded
            if ext is not None
        )

        for key, handler in self._registered.items():
            if key in excluded:
                continue
            handler()
            # handler(change, payload)

    # --- iter, sugar, and extended functionality ---

    def __iter__(self) -> Iterator[T]:
        return ListStateIterator(self, self._source)

    def __reversed__(self) -> Iterator[T]:
        return ListStateIterator(self, self._source, reversed=True)

    def iter(self, reversed: bool = False) -> Iterator[T]:
        return reversed(self._source) if reversed else iter(self._source)

    def __enter__(self) -> ListState:
        # print(f"{self}.__enter__()")
        self._change_nesting += 1
        return self._source

    def __exit__(self, *_) -> None:
        # print(f"{self}.__exit__{_}")

        assert self._change_nesting, f"internal error or incorrect use of {self}"

        self._change_nesting -= 1

        if self._change_nesting == 0:
            # self._static_souce = tuple(self._source)
            self._alert_on_change(excluded=self._change_guard)
            self._change_guard.clear()

        assert self._change_nesting >= 0, self._change_nesting

    # def __getattr__(self, name: str) -> Any:
    #     if self._change_guard == 0:
    #         raise RuntimeError(
    #             f"{self} not used in change, use `with {self}: ...` or "
    #             + f"decorate the method with `@changes({self})`"
    #         )
    #     else:
    #         return getattr(self._source, name)


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
