from tg_gui_core import _Screen_

from typing import Callable

class Screen(_Screen_):
    """
    A wrapper for the implementaiton specific primative that represnet sthe base frame
    a gui tree is built within
    """

    def __init__(self, default_margin=..., *args, **kwargs): ...
