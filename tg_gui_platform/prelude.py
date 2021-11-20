from tg_gui_core import Widget, isoncircuitpython
from .styling import Theme, align
from .button import Button
from .label import Label

from ._platform_.impl import Screen, prelude as _prelude_impl

try:
    from typing import Callable, ClassVar, Any
except:
    pass

# --- setup and globals ---

__default_theme_inst: None | Theme = None


def __make_default_theme() -> Theme:
    global __default_theme_inst

    if __default_theme_inst is not None:
        dflt_theme = __default_theme_inst
    else:
        __default_theme_inst = dflt_theme = Theme(
            {
                Button: dict(
                    # eventaully these will be system colors like color.system_midgrnd
                    style=dict(
                        fill=0x505050,
                        text=0xFFFFFF,
                        active_fill=0x808080,
                        active_text=0xFFFFFF,
                    ),
                    radius=100,
                    size=1,
                    fit_to_text=False,
                ),
                Label: dict(
                    style=dict(color=0xFFFFFF),
                    size=1,
                    align=align.center,
                ),
            }
        )

    return dflt_theme


def main(
    screen: Screen,
    theme: Theme,
    size: None | tuple[int, int] = None,
) -> Callable[[Widget], Widget]:

    rootwid = Root(
        screen=screen,
        theme=theme,
        size=(
            size
            if size is not None
            else _prelude_impl._generate_default_size_from_screen(screen)
        ),
    )

    def _main_startup(wid: Widget) -> Widget:
        assert wid._is_app_ is True
        ret = rootwid(wid)
        rootwid._std_startup_()
        return ret

    return _main_startup


# --- interface ---

from tg_gui_core.container import superior, app

if isoncircuitpython():
    from tg_gui_core.container import self

    # tg_gui_std requires a .fget method on property, circuitpython does not have this
    from .pure_python_property import property

    # TODO: consider pure_python_property this into builints?
    # (tho the purpose of prelude is to avoid that soo...)


class default:
    def __init__(self) -> None:
        raise TypeError("cannot create instances of default")

    screen: ClassVar[Callable[..., Screen]]
    theme: ClassVar[Callable[[], Theme]]


default.screen = _prelude_impl.default_screen
default.theme = __make_default_theme

from ._platform_ import guiexit
from tg_gui_core import application

from tg_gui_core import *
from tg_gui_std import *
