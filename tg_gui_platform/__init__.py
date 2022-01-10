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

# explicitly not # from __future__ import annotations

from tg_gui_core import *
from .platform import _platform_, guiexit


# --- start attribute guard ---
# add nonsense values for setup to ensure they are not used
Widget._offer_priority_ = None  # type: ignore
Widget._reserve_space_ = None  # type: ignore
Widget._self_sizing_ = None  # type: ignore

# --- start interface ---

Screen = _platform_.Screen
prelude = _platform_.prelude

# platform dependent
from .button import Button
from .label import Label

# --- end interface ---


# --- remove attribute guard ---
# these are the values
Widget._offer_priority_ = 0  # type: ignore
Widget._reserve_space_ = False  # type: ignore
Widget._self_sizing_ = False  # type: ignore
