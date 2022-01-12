import tg_gui_core

from tg_gui_core import isoncircuitpython

# This file determines what platform the std libaray should use and
# import the libaray interface for that platform

from tg_gui_core import isoncircuitpython
import sys

__all__ = ("isoncircuitpython", "impl", "prelude")

_python_impl_name = sys.implementation.name
_supported_desktop_impl_names = ("cpython",)


if isoncircuitpython():
    import tg_gui_platform_displayio as _platform_  # type: ignore

elif _python_impl_name in _supported_desktop_impl_names:
    import tg_gui_platform_qt as _platform_  # type: ignore

else:
    raise NotImplementedError(
        f"TG-Gui-Std does not yet support the `{_python_impl_name}` implementation of python"
    )

sys.modules[f"{__name__}._platform_"] = _platform_
