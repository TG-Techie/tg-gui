from tg_gui.core import Pixels, RootWidget, platform_support
from typing import Protocol

class NativeElement(Protocol):
    pass

class NativeContainer(NativeElement):
    pass

class NativeRootContainer(NativeContainer):
    pass

class Platform(platform_support._Platform_):
    # see /tg_gui/core/platform_support.py: _Platform_ for docs
    def run(self) -> None: ...
    @classmethod
    def default(cls) -> Platform: ...
    def default_size(self) -> tuple[Pixels, Pixels]: ...
    def new_container(self, dimensions: tuple[Pixels, Pixels]) -> NativeContainer: ...
    def init_native_root_container(
        self,
        dimensions: tuple[Pixels, Pixels],
    ) -> NativeRootContainer: ...
    def nest_element(
        self,
        container: NativeContainer,
        element: NativeElement,
    ) -> NativeContainer: ...
    def unnest_element(
        self,
        container: NativeContainer,
        element: NativeElement,
    ) -> None: ...
    def set_relative(
        self,
        container: NativeContainer,
        element: NativeElement,
        position: tuple[Pixels, Pixels],
    ) -> None: ...
    def show_element(self, element: NativeElement) -> None: ...
    def hide_element(self, element: NativeElement) -> None: ...
