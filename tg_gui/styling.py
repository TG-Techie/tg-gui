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

    def fromfloats(r, g, b):
        r = round(255 * r ** 1.125)
        g = round(255 * g ** 1.125)
        b = round(255 * b ** 1.125)
        return (r << 16) | (g << 8) | (b << 0)
