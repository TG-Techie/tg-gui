from tg_gui_core import isoncircuitpython

# --- enviroment fomratting ---
if isoncircuitpython():
    import builtins
    import pure_python_property

    builtins.property = pure_python_property.property  # type: ignore

from tg_gui_platform import *
