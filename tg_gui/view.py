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


from tg_gui_core import center, declarable, Widget
from .layout import Layout

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import *


@declarable
class View(Layout):

    body: ClassVar[Callable[[], Widget]]

    def __init__(self, **kwargs):
        raise NotImplementedError
        super(View, self).__init__(**kwargs)

        self._widget = self._chek_and_make_body()

    def _on_nest_(self):
        super()._on_nest_()
        self._nest_(self._widget)

    def _layout_(self):
        self._widget(center, self.dims)

    def _chek_and_make_body(self):
        cls = type(self)
        if not hasattr(cls, "body"):
            raise AttributeError(f"{cls} must define a body property")

        if callable(cls.body):
            if callable(cls.body) and not isinstance(cls.body, Widget):
                return cls.body()
            elif isinstance(cls.body, Widget):
                raise TypeError(
                    f"{cls}.body may not be a widget, got {cls.body}. "
                    + "try putting `lambda:` in front of it or using a propery"
                )
            else:
                pass  # fall thorugh
        elif isinstance(cls.body, property):
            wid = self.body
            assert isinstance(
                wid, Widget
            ), f"@property {cls}.body must be a Widget, got {wid} from {self}.body"
            return wid
        else:
            pass  # fall through

        raise TypeError(
            f"{cls}.body must be a function or a property that returns a Widget, got {cls.body}"
        )

    if not TYPE_CHECKING:

        @property
        def body(self):
            raise NotImplementedError(
                f"{type(self).__name__}.body must [TODO: add more erro message]"
            )
