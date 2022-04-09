from __future__ import annotations

from ._platform_.platform import Platform
from .core import ContainerWidget, Pixels, RootWidget, iswidgetclass

from typing import TYPE_CHECKING, TypeVar, Generic, overload


_MainWidget = TypeVar("_MainWidget", bound=ContainerWidget)

if TYPE_CHECKING:
    from typing import Callable, Type, Literal


@overload
def main(
    cls: Type[_MainWidget],
) -> RootWidget[_MainWidget]:
    ...


@overload
def main(
    *,
    platform: Platform | None = ...,
    size: tuple[Pixels, Pixels] | None = ...,
    setup: Literal[True] = True,
) -> Callable[[Type[_MainWidget]], RootWidget[_MainWidget]]:
    ...


@overload
def main(
    *,
    platform: Platform | None = ...,
    setup: Literal[False] = ...,
) -> Callable[[Type[_MainWidget]], RootWidget[_MainWidget]]:
    ...


def main(
    cls: Type[_MainWidget] | None = None,
    *,
    platform: Platform | None = None,
    size: tuple[Pixels, Pixels] | None = None,
    setup: bool = True,
) -> RootWidget | Callable[[Type[_MainWidget]], RootWidget[_MainWidget]]:
    """
    a wrapper for for widget to run it as the main widget in a window or UI root
    This qualifies as a widget wrapper, additional decotation with @widget is not needed
    """
    if __debug__ and setup is False:
        assert (
            size is None
        ), f"setup and size are mutually exclusive, got setup=False and size={size}"

    platform = platform or Platform.default()
    size = size or platform.default_size()

    if cls is None:
        return lambda cls: _main(cls, platform=platform, size=size, setup=setup)
    else:
        return _main(cls, platform=platform, size=size, setup=setup)


def _main(
    cls: Type[_MainWidget],
    *,
    platform: Platform,
    size: tuple[Pixels, Pixels],
    setup: bool,
) -> RootWidget:
    """
    a wrapped for for widget to run it as the main widget in a window or UI root
    """
    assert iswidgetclass(cls), f"{cls} is not a widget class, has bases {cls.__bases__}"

    mainwidget = cls()
    root = RootWidget(mainwidget, platform=platform)
    if setup:
        root.setup(size=size)

    return root
