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

import gc
from ._shared import uid
from .base import Widget
from .container import Container
from .base import _Screen_


class Root(Container):

    _theme_ = None

    def __init__(
        self,
        *,
        screen: _Screen_,
        size: tuple[int, int],
        theme,
        **kwargs,
    ):
        assert len(size) == 2, f"expected two dimensions found, {size}"

        self._id_ = uid()

        self._screen_ = screen

        self._size_ = size
        self._native_ = None
        self._theme_ = theme

        self._is_shown = False

        self._inst_kwargs = kwargs
        self._nested_: list[Widget] = []
        self._wrapped_widget = None

        screen.root = self

    _margin_ = property(lambda self: 0)  # type: ignore
    _phys_size_ = property(lambda self: self._size_)  # type: ignore

    def __call__(self, widinst):
        self._wrapped_widget = root_wid_inst = widinst
        self._nest_(root_wid_inst)
        return root_wid_inst

    # _size_ is raw, exposed

    # possibly make settable in the future
    _coord_ = property(lambda self: (0, 0))  # type: ignore
    _rel_coord_ = property(lambda self: (0, 0))  # type: ignore
    _phys_coord_ = property(lambda self: (0, 0))  # type: ignore

    @property
    def _superior_(self):
        return None

    @property
    def wrapped(self):
        return self._wrapped_widget

    def isnested(self):
        # since a this is a root it does nto need to be nested,
        #   this returns true indicat the nesting stage is "complete"
        #   for this object, even though no calcuation is needed for it
        return True

    def _std_startup_(self):
        # self does not need to be formated as it already has form and position
        self._build_(None)
        self._place_(None)
        gc.collect()
        self._show_()

    def _build_(self, check):
        assert check is None  # exists to ensure proper use
        # print(self, self._wrapped_widget)
        self._screen_.on_widget_build(self)
        self._wrapped_widget._build_(self._size_)
        self._screen_.on_container_build(self)

    def _demolish_(self):
        self._wrapped_widget._demolish_()
        self._screen_.on_widget_demolish(self)
        self._screen_.on_container_demolish(self)

    def _place_(self, check):
        assert check is None  # exists to ensure proper use
        # print(self, self._wrapped_widget)
        self._wrapped_widget._place_((0, 0))

    def _pickup_(self):
        self._wrapped_widget._pickup_()

    def _show_(self):
        self._is_shown = True
        self._wrapped_widget._show_()

    def _hide_(self):
        self._is_shown = False
        self._wrapped_widget._hide_()
