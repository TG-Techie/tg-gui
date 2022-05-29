from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Any, TypeGuard, overload, ClassVar
    from typing_extensions import Self, LiteralString

from tg_gui_core.shared import IsinstanceBase

# OPTIMIZATION: # from tg_gui_core.implementation_support import isoncircuitpython
from .stateful import State


class Color(int, IsinstanceBase):

    white: ClassVar[Color | State[Color]] = 0xFFFFFF  # type: ignore[override]
    black: ClassVar[Color | State[Color]] = 0x000000  # type: ignore[override]
    gray: ClassVar[Color | State[Color]] = 0x808080  # type: ignore[override]
    lightgray: ClassVar[Color | State[Color]] = 0xC0C0C0  # type: ignore[override]
    darkgray: ClassVar[Color | State[Color]] = 0x404040  # type: ignore[override]

    # TODO:P revise these or change them per-platform
    red: ClassVar[Color | State[Color]] = 0xFF0000  # type: ignore[override]
    orange: ClassVar[Color | State[Color]] = 0xFFA500  # type: ignore[override]
    yellow: ClassVar[Color | State[Color]] = 0xFFFF00  # type: ignore[override]
    green: ClassVar[Color | State[Color]] = 0x00FF00  # type: ignore[override]
    blue: ClassVar[Color | State[Color]] = 0x0000FF  # type: ignore[override]
    purple: ClassVar[Color | State[Color]] = 0x800080  # type: ignore[override]

    # --- system colors ---
    # text forground
    foreground: ClassVar[Color | State[Color]] = 0xFFFFFF  # type: ignore[override]
    fill: ClassVar[Color | State[Color]] = lightgray  # type: ignore[override]

    def __new__(cls, rgb_value: int) -> Color:
        """
        :param value: The int to convert to a Color.
        (lie to the type system and check it with IsinstanceBase's _inst_isinstance_check_)
        """
        assert isinstance(rgb_value, int)
        if not (0 <= rgb_value <= 0xFFFFFF):
            raise TypeError(
                f"Color must be an integer between 0 and 0xFFFFFF, not {rgb_value}"
            )
        # OPTIMIZATION: # if isoncircuitpython():
        return rgb_value  # type: ignore[return-value]
        # OPTIMIZATION: # else:
        # OPTIMIZATION: #     return int.__new__(cls, rgb_value)

    # OPTIMIZATION: # if isoncircuitpython():
    @classmethod
    def _inst_isinstance_check_(cls, __instance: Any) -> TypeGuard[Self]:
        return isinstance(__instance, int) and 0 <= __instance <= 0xFFFFFF

    if TYPE_CHECKING:

        @overload
        @classmethod
        def fromrgb(cls, r: int, g: int, b: int) -> Color:
            ...

        @overload
        @classmethod
        def fromrgb(cls, r: float, g: int, b: int) -> Color:
            ...

    @classmethod
    def fromrgb(cls, r: int | float, g: int | float, b: int | float) -> Color:
        """
        Combines the red, green, and blue components into a single integer
        :param r: red component, int (0-255) or float (0.0-1.0)
        :param g: green component, int (0-255) or float (0.0-1.0)
        :param b: blue component, int (0-255) or float (0.0-1.0)
        :return: the combined color as in int
        """
        r = int(r * 255) if isinstance(r, float) else r
        g = int(g * 255) if isinstance(g, float) else g
        b = int(b * 255) if isinstance(b, float) else b
        return cls((r << 16) | (g << 8) | (b << 0))

    @classmethod
    def fromhex(cls, hex: LiteralString) -> Color:
        """
        Takes a hex string of the form '#RRGGBB', '#RGB', format and returns a color
        :param hex: the hex string
        :return: the color as an int
        """
        _hex = str(hex)
        assert hex.startswith("#") and (
            len(_hex) in (7, 4)
        ), f"hex string must be '#RRGGBB' or '#RGB' format, not '{hex}'"

        # remove the #
        src: str = _hex[1:]
        # if it is 3 characters, double each character
        if len(src) == 2:
            src = src[0] * 2 + src[1] * 2 + src[2] * 2

        return cls(int(src, 16))

    def __int__(self) -> int:
        return self  # type: ignore[return-value]
