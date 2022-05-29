# TODO: convert tests/ to pytest

from tg_gui import platform


assert platform.__name__ == "tg_gui._platform_qt_", (
    f"platform.__name__ is not 'tg_gui._platform_qt_', found {platform.__name__!r}, "
    "On cpython, this should import 'tg_gui_core._platform_qt_' and alias it to 'tg_gui.platform'."
)
