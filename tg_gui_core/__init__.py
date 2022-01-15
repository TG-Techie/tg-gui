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

# explicity not # from __future__ import annotations # yet!

import sys

# -- start exposed api imports ---

# base classes and application environment
from ._implementation_support import (
    guiexit,
    isoncircuitpython,
    enum_compat,
    use_typing,
)

from typing import TYPE_CHECKING

from .base import (
    application,
    Widget,
)

from .container import Container
from .layout import Layout

from .stateful import (
    State,
    DerivedState,
    Bindable,
    Identifiable,
)


from .position_specifiers import (
    PositionSpecifier,
    ConstantPosition,
    centerto,
    leftof,
    rightof,
    below,
    above,
    center,
    top,
    bottom,
    left,
    right,
)

from .dimension_specifiers import (
    DimensionSpecifier,
    DimensionExpression,
    DimensionExpressionConstructor,
    ratio,
    height,
    width,
)


# --- std lib and impl tool ---

# classes and functions for making widget classes
from ._implementation_support import enum_compat
from .base import uid, UID, _Screen_
from .root_widget import Root
from .widget_builder import Declarable
from .styled_widget import StyledWidget, align, Color, color
from .theming import Theme, themedwidget

if TYPE_CHECKING:
    from typing import Any

    class _SelfStub:
        def __getattr__(self) -> Any:
            return None

    self = _SelfStub()
