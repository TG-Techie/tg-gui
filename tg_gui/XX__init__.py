import sys
from tg_gui_core import *

from . import _platform_setup_

# is this a hack? yes! (again, it's @TG-Techie on github)
sys.modules[f"{__name__}._platform_setup_"] = _platform_setup_

from . import platform as _platform
