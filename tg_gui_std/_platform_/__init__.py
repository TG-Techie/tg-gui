# This file determines what platform the std libaray should use and
# import the libaray interface for that platform

from tg_gui_core import isoncircuitpython
import sys

__all__ = ("isoncircuitpython", "impl", "prelude")

_python_impl_name = sys.implementation.name
_supported_desktop_impl_names = ("cpython",)


if isoncircuitpython():
    from . import displayio_impl as impl  # type: ignore
    from supervisor import reload as guiexit
elif _python_impl_name in _supported_desktop_impl_names:
    from . import qt_impl as impl  # type: ignore
    from sys import exit as guiexit
else:
    raise NotImplementedError(
        f"TG-Gui-Std does not yet support the `{_python_impl_name}` implementation of python"
    )

prelude = impl.prelude

# add the impl / prelude as an importable module
sys.modules[f"{__name__}.impl"] = impl
sys.modules["_tg_gui_std_impl"] = impl
sys.modules[f"{__name__}.prelude"] = prelude
sys.modules["_tg_gui_std_impl_prelude"] = prelude
