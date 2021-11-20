from tg_gui_core import *
from ._platform_ import impl

Screen = impl.Screen

# add nonsense values for setup to ensure they are not used
Widget._offer_priority_ = None  # type: ignore
Widget._reserve_space_ = None  # type: ignore
Widget._self_sizing_ = None  # type: ignore


from .styling import (
    align,
    StyledWidget,
    Theme,
    SubTheme,
    Style,
    DerivedStyle,
)

# platform dependent
from .button import Button
from .label import Label

# format for usage
Widget._offer_priority_ = 0  # type: ignore
Widget._reserve_space_ = False  # type: ignore
Widget._self_sizing_ = False  # type: ignore


# --- environment formatting ---

# circuitpython does not expose the fset and fget attributes on property objects
# some tg_gui values may require access to those methods
if isoncircuitpython():
    import builtins
    import pure_python_property

    builtins.property = pure_python_property.property  # type: ignore
