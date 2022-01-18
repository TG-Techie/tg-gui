from __future__ import annotations

from .core import PlatformWidget, buildattr, themedattr, Pixels, widget
from .core._platform_support_ import platformwidget

from . import _platform_
from .styling import Color, color

from typing import TYPE_CHECKING

# annotation-only import
if TYPE_CHECKING:
    from typing import Callable


@platformwidget(_platform_.button)
class CapsuleButton(PlatformWidget):

    text: str = buildattr(repr=True)
    action: Callable[[], None] = buildattr()

    radius: float = themedattr(default=1.0)
    fill: Color = themedattr(default=color.system_fill)
    foreground: Color = themedattr(default=color.system_foreground)
    active_fill: Color = themedattr(default=color.system_active_fill)
    active_foreground: Color = themedattr(default=color.system_active_foreground)


# future proofing
@widget
class Button(CapsuleButton):
    pass
