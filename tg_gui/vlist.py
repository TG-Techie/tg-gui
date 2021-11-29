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

from tg_gui_core import Container, Widget, isoncircuitpython, Constant
from .liststate import ListState, _ListStateIterator, _LSIterMode

from typing import TYPE_CHECKING

if TYPE_CHECKING or not isoncircuitpython():
    from typing import Generic, TypeVar, Callable, overload, Type, Generator

T = TypeVar("T")

GeneratorType = type(_ for _ in ())


class VList(Container, Generic[T]):

    if TYPE_CHECKING:

        @overload
        def __init__(
            cls: Type[VList],
            liststate: ListState[T],
            factory: Callable[[T], Widget],
        ) -> None:
            ...

        @overload
        def __init__(cls: Type[VList], __gen: Generator[Widget, None, None]) -> None:
            ...

        def __init__(cls: Type[VList], *_, **__) -> VList:
            raise RuntimeError("this should exist at runtime! ... How did you do this?")

    else:

        def __init__(
            self,
            liststate: ListState[T],
            factory: None | Callable[[T], Widget] = None,
        ) -> None:

            if isinstance(liststate, GeneratorType) and factory is None:
                liststate, factory = self._from_genetator(liststate)

            assert factory is not None, f"missing 'factory' (2nd) argument"

            self._source = liststate
            self._factory = factory

            self._ids_to_widgets = [
                (hash(model), factory(model)) for model in liststate
            ]

            super().__init__()

    def _apply_list_change_event(
        self,
        change: Constant,  # ListChange
        indices: None | int | tuple[int] = None,
    ) -> None:
        raise NotImplementedError()

    @classmethod
    def _from_genetator(cls: Type[VList], gen: Generator[Widget, None, None]) -> VList:

        factory: _ListStateIterator[T] = ListState.get_last_lsiter_sugar()
        assert factory._mode is _LSIterMode.unconfiged

        liststate = factory._configure_as_factory_(gen)
        assert factory._mode is _LSIterMode.factory

        return cls(liststate, factory)
