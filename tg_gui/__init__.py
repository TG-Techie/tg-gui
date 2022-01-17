import sys as _sys

from .core import *

from typing import TYPE_CHECKING

# --- set the concrete platform implementation ---
if TYPE_CHECKING:
    from . import _platform_
elif isoncircuitpython():
    from . import _platform_displayio_ as _platform_  # type: ignore[no-redef]
else:
    import _platform_qt_ as _platform_  # type: ignore[no-redef]

_sys.modules[f"{__name__}._platform_"] = _platform_

# --- etc... ? ---
