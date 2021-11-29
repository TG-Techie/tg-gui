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
from .liststate import ListState

# from .liststate import ListState
if not isoncircuitpython():
    from typing import Generic, TypeVar, Callable

T = TypeVar("T")


class VList(Container, Generic[T]):
    def __init__(
        self,
        liststate: ListState[T],
        model_to_widget: Callable[[T], Widget],
    ) -> None:
        self._source = liststate
        self._model_to_widget = model_to_widget

        self._ids_to_widgets = [
            (hash(model), model_to_widget(model)) for model in liststate
        ]

        super().__init__()

    def _apply_list_change_event(
        self,
        change: Constant,  # ListChange
        indices: None | int | tuple[int] = None,
    ) -> None:
        raise NotImplementedError()
