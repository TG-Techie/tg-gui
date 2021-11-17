from tg_gui_core import ConstantGroup
from .styled_widget import StyledWidget
from .theming import Theme, SubTheme, themedwidget
from .style import Style
from .style import DerivedStyle

align = ConstantGroup(
    "align",
    (
        "leading",
        "center",
        "trailing",
    ),
)
