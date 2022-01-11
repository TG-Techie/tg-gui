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


from tg_gui_core import Container, declarable


@declarable
class Layout(Container):
    def _build_(self, dim_spec):
        super(Container, self)._build_(dim_spec)
        self._screen_.on_container_build(self)  # platform tie-in

    def _place_(self, pos_spec):
        super(Container, self)._place_(pos_spec)

        if hasattr(self, "_layout_"):
            self._layout_()
        elif hasattr(self, "_any_"):
            print(
                f"WARNING: ._any_(...) for layout will be depricated soon, use ._layout_(...) instead"
            )
            self._any_()
        else:
            raise RuntimeError(f"{self} has no ._layout_ method, define one")

        self._screen_.on_container_place(self)  # platform tie-in

    def _show_(self):
        super(Container, self)._show_()
        for widget in self._nested_:
            widget._show_()

    def _layout_(self):
        raise NotImplementedError(
            f"layout methods must be written for subclasses of Layout"
        )

    def _any_(self):
        raise NotImplementedError(
            f"layout methods must be written for subclasses of Layout"
        )
