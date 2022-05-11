# import tg_gui_core first incase we are running on
import tg_gui_core

from typing import TYPE_CHECKING

from sys import implementation as _implementation

if TYPE_CHECKING or _implementation.name == "cpython":
    from .._platform_qt_ import *
elif _implementation.name == "circuitpython":
    from .._platform_displayio_ import *
else:
    raise NotImplementedError(
        "tg_gui does not have an implementation for this python implementation"
        + f" ({_implementation.name}) and/or platform"
    )
