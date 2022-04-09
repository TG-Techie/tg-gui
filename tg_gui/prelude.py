from __future__ import annotations

from ._platform_.platform import Platform
from .core import ContainerWidget, Pixels, RootWidget, widget

from typing import TYPE_CHECKING, TypeVar, Generic


_MainWidget = TypeVar("_MainWidget", bound=ContainerWidget)

if TYPE_CHECKING:
    from typing import overload, Callable, Type, Literal

    @overload
    def main(
        platform: Platform | None = ...,
        size: tuple[Pixels, Pixels] | None = ...,
    ) -> Callable[[Type[_MainWidget]], _MainWidget]:
        ...

    @overload
    def main(
        platform: Platform | None = ...,
        setup: bool = ...,
    ) -> Callable[[Type[_MainWidget]], _MainWidget]:
        ...

    @overload
    def main(cls: Type[_MainWidget]) -> _MainWidget:
        ...

    def main(*_, **__):
        raise NotImplementedError

else:

    def main(
        cls: Type[_MainWidget] | None = None,
        *,
        platform: Platform | None = None,
        size: tuple[Pixels, Pixels] | None = None,
        setup: bool = True,
    ) -> _MainWidget:
        """
        a wrapped for for widget to run it as the main widget in a window or UI root
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
) -> _MainWidget:
    """
    a wrapped for for widget to run it as the main widget in a window or UI root
    """
    widget(cls)

    mainwidget = cls()
    root = RootWidget(mainwidget, platform=platform)
    if setup:
        root.setup(size=size)

    return mainwidget
