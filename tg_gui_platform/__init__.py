from tg_gui_core import *
from ._platform_impls import _platform_


# --- start attribute guard ---
# add nonsense values for setup to ensure they are not used
Widget._offer_priority_ = None  # type: ignore
Widget._reserve_space_ = None  # type: ignore
Widget._self_sizing_ = None  # type: ignore

# --- start interface ---

Screen = _platform_.Screen
prelude = _platform_.prelude

# platform dependent
from .button import Button
from .label import Label

# --- end interface ---


# --- remove attribute guard ---
# these are the values
Widget._offer_priority_ = 0  # type: ignore
Widget._reserve_space_ = False  # type: ignore
Widget._self_sizing_ = False  # type: ignore
