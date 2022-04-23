import sys as _sys


from .core import *
from . import core as _core

from typing import TYPE_CHECKING

# TYPE_CHECKING should not be exported but aslo cannot be aliased so
#   it is deleted later

# --- set the concrete platform implementation ---

if TYPE_CHECKING:
    from . import _platform_
elif _core.implementation_support.isoncircuitpython():
    from . import _platform_displayio_ as _platform_  # type: ignore[no-redef]
else:
    from . import _platform_qt_ as _platform_  # type: ignore[no-redef]
# do not export TYPE_CHECKING
del TYPE_CHECKING

# --- set the concrete platform implementation and make it importable ---
_sys.modules[f"{__name__}._platform_"] = _platform_


# --- prelude info ---
# import the additional exported objects

from .prelude import main

# --- etc... ? ---
from .view import View, ViewBody
from .stacks import VStack

# --- platform widgets ---
from .button import Button
