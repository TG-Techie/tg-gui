from tg_gui_core import *
from tg_gui_std import *
import time
import sys


screen = Screen()

theme = Theme(
    {
        Button: dict(
            # eventaully these will be system colors like color.system_midgrnd
            style=dict(
                fill=0x505050, text=0xFFFFFF, active_fill=0x808080, active_text=0xFFFFFF
            ),
            radius=100,
            size=1.5,
            fit_to_text=False,
        ),
        Label: dict(
            style=dict(color=0xFFFFFF),
            size=1.5,
            align=align.center,
        ),
    }
)

main = lambda wid: (
    rootwid := Root(
        screen=screen,
        theme=theme,
        size=(480, 480),
    )(wid),
    rootwid._superior_._std_startup_(),
)[0]
