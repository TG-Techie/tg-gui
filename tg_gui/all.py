from tg_gui_core import *
from ._platform_setup_ import *
from . import platform

if annotation_only():
    from typing_extensions import Self

from .view import View

from platform.text import Text
