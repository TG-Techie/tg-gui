from __future__ import annotations


from .widget import Widget
from .themeing import Theme

from typing import TYPE_CHECKING
from abc import ABC, abstractproperty

# annotation-only imports
if TYPE_CHECKING:
    from typing import ClassVar, Iterable


class SuperiorWidget(Widget):
    # TODO: give that an antucal name... but not 'Container'

    _theme_: Theme | None = None

    # _environment_: Environment | ClassVar[Environment] | None = None

    @abstractproperty
    def _nested_widgets_(self) -> Iterable[Widget]:
        raise NotImplementedError
