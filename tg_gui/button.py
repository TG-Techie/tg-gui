from __future__ import annotations

from .core import PlatformWidget, InitAttr, StatefulAttr
from .core._platform_support_ import requiredplatformmethod, platformwidget
from . import _platform_

from typing import TYPE_CHECKING

# annotation-only import
if TYPE_CHECKING:
    from typing import Callable


@platformwidget(_platform_.button)
class CapsuleButton(PlatformWidget):

    text: str = BuildAttr(positional=True)  # type: ignore[assignment]
    action: Callable[[], None] = BuildAttr()  # type: ignore[assignment]
    radius: float = ThemedAttr(default=1.0, build=True)  # type: ignore[assignment]

    fill: Color = ThemedAttr(default=color.system_fill)  # type: ignore[assignment]
    foreground: Color = ThemedAttr(default=color.system_foreground)  # type: ignore[assignment]
    active_fill: Color = ThemedAttr(default=color.system_active_fill)  # type: ignore[assignment]
    active_foreground: Color = ThemedAttr(default=color.system_active_foreground)  # type: ignore[assignment]
