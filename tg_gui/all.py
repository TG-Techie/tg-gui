from tg_gui_core import *
from ._platform_setup_ import *
from . import platform

if TYPE_CHECKING:
    from typing_extensions import Self

from .view import View

from .platform.text import Text
