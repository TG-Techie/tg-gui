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
from tg_gui_core.layout import Layout
from tg_gui_core.widget_builder import WidgetBuilder, _widget_builder_cls_format

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import *


@declarable
class View(Layout):

    body: ClassVar[Callable[[], Widget]]

    def __new__(cls, *args, **kwargs):
        assert (
            cls is not View
        ), f"View is an abstract class, {cls} cannot be instantiated"
        assert hasattr(cls, "body"), "View must have a body widget builder"

        # TODO: make this a better check
        if not isinstance(cls.body, WidgetBuilder):
            _widget_builder_cls_format(cls)

        return super().__new__(cls)

    def _layout_(self):
        self.body(center, self.dims)
