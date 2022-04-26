from __future__ import annotations

from ._platform_.platform import Platform
from .core import ContainerWidget, Pixels, RootWidget, iswidgetclass

from typing import TYPE_CHECKING, TypeVar, Generic, overload


_MainWidget = TypeVar("_MainWidget", bound=ContainerWidget)

if TYPE_CHECKING:
    from typing import Callable, Type, Literal


def main(
    cls: Type[_MainWidget],
    *,
    platform: Platform | None = None,
    setup: bool = True,
    **kwargs,
) -> RootWidget[_MainWidget]:
    """
    a wrapper for for widget to run it as the main widget in a window or UI root
    This qualifies as a widget wrapper, additional decotation with @widget is not needed
    """

    platform = platform or Platform.default()

    assert iswidgetclass(cls), f"{cls} is not a widget class, has bases {cls.__bases__}"

    mainwidget = cls()
    root = RootWidget(mainwidget, platform=platform, **kwargs)
    if setup:
        root.setup()

    return root
