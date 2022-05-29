# import tg_gui_core before typing for circuitpython compatibility
# this only needs ot happen once
import tg_gui_core

from typing import TYPE_CHECKING

from sys import implementation as _implementation, modules as _sys_modules


if TYPE_CHECKING or _implementation.name == "cpython":
    from .. import _platform_qt_ as _platform_  # type: ignore
    from .._platform_qt_ import *
elif _implementation.name == "circuitpython":
    from .. import _platform_displayio_ as _platform_  # type: ignore
    from .._platform_displayio_ import *
else:
    raise NotImplementedError(
        "tg_gui does not have an implementation for this python implementation"
        + f" ({_implementation.name}) and/or platform"
    )

_sys_modules["tg_gui.platform"] = _platform_
