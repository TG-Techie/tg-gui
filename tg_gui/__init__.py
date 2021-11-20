from tg_gui_core import isoncircuitpython
import tg_gui_platform

# --- enviroment fomratting ---
if isoncircuitpython():
    import builtins
    from . import pure_python_property

    builtins.property = pure_python_property.property  # type: ignore
