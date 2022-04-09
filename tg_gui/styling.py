from tg_gui.core import State

Color = int


class color:
    # TODO: consider make ready only using proerties and lambdas vs performance
    red: Color = 0xFF0000
    orange: Color = 0xFFA500
    yellow: Color = 0xFFFF00
    green: Color = 0x00FF00
    lightgreen: Color = 0xA0FFA0
    blue: Color = 0x0000FF
    purple: Color = 0xCC8899

    white: Color = 0xFFFFFF
    lightgray: Color = 0xC4C4C4
    gray: Color = 0x909090
    darkgray: Color = 0x606060
    black: Color = 0x000000

    # TODO: make these states
    system_fill: Color | State[Color] = 0x909090
    system_foreground: Color | State[Color] = 0xFFFFFF
    system_active_fill: Color | State[Color] = 0x505050
    system_active_foreground: Color | State[Color] = 0xFFFFFF
    system_background: Color | State[Color] = 0x000000

    @staticmethod
    def fromfloats(red: float, green: float, blue: float) -> Color:
        """
        Creates a color from red, green, and blue as floats between 0 and 1.

        :param red: red component
        :param green: green component
        :param blue: blue component
        :return: combined color
        """
        assert 0 <= red <= 1, f"r must be between 0 and 1, got {red}"
        assert 0 <= green <= 1, f"g must be between 0 and 1, got {green}"
        assert 0 <= blue <= 1, f"b must be between 0 and 1, got {blue}"
        # use ** 1.125 as a faux gamma correction
        red = round(255 * red ** 1.125)
        green = round(255 * green ** 1.125)
        blue = round(255 * blue ** 1.125)
        return (red << 16) | (green << 8) | (blue << 0)

    @staticmethod
    def fromint(red: int, green: int, blue: int) -> Color:
        """
        Creates a color from red, green, and blue as integers between 0 and 255.

        :param red: red component
        :param green: green component
        :param blue: blue component
        :return: combined color
        """
        assert 0 <= red <= 255, f"r must be between 0 and 255, got {red}"
        assert 0 <= green <= 255, f"g must be between 0 and 255, got {green}"
        assert 0 <= blue <= 255, f"b must be between 0 and 255, got {blue}"
        return (red << 16) | (green << 8) | (blue << 0)
