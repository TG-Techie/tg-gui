from __future__ import annotations


from .widget import Widget
from .themeing import Theme

from typing import TYPE_CHECKING
from abc import ABC, abstractmethod, abstractproperty

# annotation-only imports
if TYPE_CHECKING:
    from typing import ClassVar, Iterable

    from .._platform_.platform import Platform, NativeContainer


class ContainerWidget(Widget, ABC):

    _theme_: Theme | None = None

    @abstractproperty
    def _native_(self) -> NativeContainer:
        raise NotImplementedError

    # _environment_: Environment | ClassVar[Environment] | None = None

    @abstractmethod
    def _nested_widgets_(self) -> Iterable[Widget]:
        raise NotImplementedError

    def _on_nest_(self, superior: ContainerWidget, platform: Platform) -> None:
        super()._nest_in_(superior, platform)
        for widget in self._nested_widgets_():
            widget._nest_in_(self, platform)

    def _on_unnest_(self, superior: ContainerWidget, platform: Platform) -> None:
        for widget in self._nested_widgets_():
            widget._unnest_from_(superior=self, platform=platform)
        return super()._unnest_from_(superior, platform)
