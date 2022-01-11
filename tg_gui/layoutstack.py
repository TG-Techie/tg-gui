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

from tg_gui_core import (
    Widget,
    Container,
    center,
    top,
    bottom,
    left,
    right,
    below,
    rightof,
    SubTheme,
)
from tg_gui_platform.button import Button

GeneratorType = type(_ for _ in ())


class _LayoutStack(Container):

    # _theme_ = SubTheme(
    #     {
    #         Button: dict(
    #             fit_to_text=False,
    #         ),
    #     }
    # )

    @property
    def _reserve_space_(self):
        print(self, self._widgets)
        return any(wid._reserve_space_ for wid in self._nested_)

    def __init__(self, *widgets: Widget, **kwargs):
        if len(widgets) == 1 and isinstance(widgets[0], GeneratorType):
            widgets = tuple(widgets[0])

        super().__init__(**kwargs)

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

        self._build_stack(suggested, sorted_widgets)

    def _place_(self, pos_spec):

        super(Container, self)._place_(pos_spec)

        # put the first widget at teh top thern stack them below that
        wid_iter = iter(self._nested_)
        previous = next(wid_iter)
        previous._place_(self._place_start)

        for widget in wid_iter:
            widget._place_(self._place_spec(previous))
            previous = widget

        self._screen_.on_container_place(self)  # platform tie-in


class VStack(_LayoutStack):
    _place_start = top
    _place_spec = below

    def _build_stack(self, suggested: tuple[int, int], widgets: list[Widget]):

        remaining_count = len(widgets)
        remaining_reserved_count = sum(
            1 if wid._reserve_space_ else 0 for wid in widgets
        )

        width, remaining_space = suggested

        for widget in reversed(widgets):
            if remaining_reserved_count > 0:
                offer = remaining_space // remaining_reserved_count
                widget._build_((width, offer))
                remaining_space -= widget.height
            else:
                widget._build_((width, remaining_space // remaining_count))
            remaining_reserved_count -= 1
            remaining_count -= 1

        self._build_exactly_(
            max(wid.width for wid in widgets),
            sum(wid.height for wid in widgets),
        )


class HStack(_LayoutStack):
    _place_start = left
    _place_spec = rightof

    def _build_stack(self, suggested: tuple[int, int], widgets: list[Widget]):

        remaining_count = len(widgets)
        remaining_reserved_count = sum(
            1 if wid._reserve_space_ else 0 for wid in widgets
        )

        remaining_space, height = suggested

        for widget in reversed(widgets):
            if remaining_reserved_count > 0:
                offer = remaining_space // remaining_reserved_count
                widget._build_((offer, height))
                remaining_space -= widget.width
            else:
                widget._build_((remaining_space // remaining_count, height))
            remaining_reserved_count -= 1
            remaining_count -= 1

        self._build_exactly_(
            sum(wid.width for wid in widgets),
            max(wid.height for wid in widgets),
        )
