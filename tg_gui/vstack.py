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

from tg_gui_core import Widget, Container, below, top, SubTheme
from tg_gui_platform.button import Button

GeneratorType = type(_ for _ in ())


class VStack(Container):

    _theme_ = SubTheme(
        {
            Button: dict(
                fit_to_text=False,
            ),
        }
    )

    def __init__(self, *widgets: Widget):
        if len(widgets) == 1 and isinstance(widgets[0], GeneratorType):
            widgets = tuple(widgets[0])
        super().__init__()

        self._widgets = widgets

    def _on_nest_(self):
        super()._on_nest_()
        for widget in self._widgets:
            self._nest_(widget)
        self._widgets = None

    def _build_(self, dim_spec):

        suggested = self._specify_dim_spec(dim_spec)
        self._screen_.on_container_build(self)  # platform tie-in

        sorted_widgets = sorted(
            self._nested_,
            key=lambda wid: (
                wid._reserve_space_,
                wid._self_sizing_,
                wid._offer_priority_,
            ),
        )

        remaining_count = len(sorted_widgets)
        remainging_reserved_count = sum(
            1 if wid._reserve_space_ else 0 for wid in sorted_widgets
        )

        width, remaining_space = suggested

        for widget in reversed(sorted_widgets):
            if remainging_reserved_count > 0:
                offer = remaining_space // remainging_reserved_count
                widget._build_((width, offer))
                remaining_space -= widget.height
            else:
                widget._build_((width, remaining_space // remaining_count))
            remainging_reserved_count -= 1
            remaining_count -= 1

        self._build_exactly_(width, sum(wid.height for wid in sorted_widgets))

    def _place_(self, pos_spec):

        super(Container, self)._place_(pos_spec)

        # put the first widget at teh top thern stack them below that
        wid_iter = iter(self._nested_)
        previous = next(wid_iter)
        previous._place_(top)

        for widget in wid_iter:
            widget._place_(below(previous))
            previous = widget

        self._screen_.on_container_place(self)  # platform tie-in
