# import tg_gui_core before typing for circuitpython compatibility
# this only needs ot happen once
import tg_gui_core as _tg_gui_core_

from typing import TYPE_CHECKING

from sys import implementation as _implementation, modules as _sys_modules


if TYPE_CHECKING or _implementation.name == "cpython":
    from .. import _platform_qt_ as _platform_  # type: ignore
elif _implementation.name == "circuitpython":
    from .. import _platform_displayio_ as _platform_  # type: ignore
else:
    raise NotImplementedError(
        "tg_gui does not have an implementation for this python implementation"
        + f" ({_implementation.name}) and/or platform"
    )

# alias the implementation for this platform to `tg_gui.platform`
assert __name__ == "tg_gui.platform", "module resolution error"
_sys_modules[__name__] = _platform_
del _implementation, _sys_modules, TYPE_CHECKING  # do not release the _platform_ module
