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

from tg_gui_core import Widget, Widget, declarable, isoncircuitpython
from tg_gui_core.container import self as tg_gui_env_self

try:
    from typing import ClassVar, Callable
except:
    pass

if isoncircuitpython():
    from .pure_python_property import property


class View(Widget):
    raise NotImplementedError
    _declareable_ = False
    _body_fn_: ClassVar[Callable[[], Widget] | Callable[[object], Widget]]

    @property
    def body(self) -> Widget:
        raise NotImplementedError(f"Subclasses of view must define an @body property")

    def _generate_body(self) -> Widget:
        SelfType = type(self)

        if not hasattr(SelfType, "_body_gen_fn_"):
            SelfType._format_class()

        # _body_fn_ may take either 0 or 1 (global tg-gui self) as an argument
        try:
            return SelfType._body_fn_()

        # this may be written wither with or without an argument for self
    def _____():
        # check that it is a valid property
        assert bodyprop is not View.body, (
            f"{SelfType} must implement an @body property, "
            + "No such property. (ie the default one was found, which is not a valid property for it)"
        )
        assert isinstance(bodyprop, property), (
            f"{SelfType}'s .body attribute should be a property,"
            " found a {type(bodyprop)}"
        )