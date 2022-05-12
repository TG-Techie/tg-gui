from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, TypeGuard, overload, ClassVar
    from typing_extensions import Self, LiteralString

from tg_gui_core.shared import IsinstanceBase
from .stateful import State

class Color(int, IsinstanceBase):
    # --- pre-defined system colors ---
    # foreground, fill
    @property
    @classmethod
    def foreground(cls) -> Color | State[Color]: ...
    @property
    @classmethod
    def fill(cls) -> Color | State[Color]: ...
    # --- pre-defined general colors ---
    # white, black, gray, lightgray, darkgray
    @property
    @classmethod
    def white(cls) -> Color | State[Color]: ...
    @property
    @classmethod
    def black(cls) -> Color | State[Color]: ...
    @property
    @classmethod
    def gray(cls) -> Color | State[Color]: ...
    @property
    @classmethod
    def lightgray(cls) -> Color | State[Color]: ...
    @property
    @classmethod
    def darkgray(cls) -> Color | State[Color]: ...
    # red, orange, yellow, green, blue, purple
    @property
    @classmethod
    def red(cls) -> Color | State[Color]: ...
    @property
    @classmethod
    def orange(cls) -> Color | State[Color]: ...
    @property
    @classmethod
    def yellow(cls) -> Color | State[Color]: ...
    @property
    @classmethod
    def green(cls) -> Color | State[Color]: ...
    @property
    @classmethod
    def blue(cls) -> Color | State[Color]: ...
    @property
    @classmethod
    def purple(cls) -> Color | State[Color]: ...
    # --- custom createation related class methods ---
    def __new__(cls, value: int) -> Color: ...
    @classmethod
    def _inst_isinstance_check_(cls, __instance: Any) -> TypeGuard[Self]: ...
    @overload
    @classmethod
    def fromrgb(cls, r: int, g: int, b: int) -> Color: ...
    @overload
    @classmethod
    def fromrgb(cls, r: float, g: int, b: int) -> Color: ...
    @classmethod
    def fromrgb(cls, r: int | float, g: int | float, b: int | float) -> Color:
        """
        Combines the red, green, and blue components into a single integer
        :param r: red component, int (0-255) or float (0.0-1.0)
        :param g: green component, int (0-255) or float (0.0-1.0)
        :param b: blue component, int (0-255) or float (0.0-1.0)
        :return: the combined color as in int
        """
        ...
    @classmethod
    def fromhex(cls, hex: LiteralString) -> Color:
        """
        Takes a hex string of the form '#RRGGBB', '#RGB', format and returns a color
        :param hex: the hex string
        :return: the color as an int
        """
        ...
    def __int__(self) -> int: ...
