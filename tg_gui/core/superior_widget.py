from __future__ import annotations

from .widget import Widget
from .themeing import Theme

from typing import TYPE_CHECKING

# annotation-only imports
if TYPE_CHECKING:
    from typing import ClassVar


class SuperiorWidget(Widget):
    # TODO: give that an antucal name... but not 'Container'

    _theme_: Theme | None = None

    # _environment_: Environment | ClassVar[Environment] | None = None

    pass
