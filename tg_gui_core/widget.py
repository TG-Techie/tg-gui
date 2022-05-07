from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar


if TYPE_CHECKING:
    from typing import ClassVar, Type, Iterator, Any, Literal
    from typing_extensions import Self
    from tg_gui.platform import Platform, NativeElement
    from .container import ContainerWidget
# ---

from abc import ABC, abstractmethod

from .shared import UID, Pixels
from .attrs import WidgetAttr, widget
from .implementation_support import Missing, isoncircuitpython


## subclasses require the @widget decorator
# @widget
class Widget(ABC):
    __is_widget_class__: ClassVar[Literal[True]] = True
    __widget_class_id__: ClassVar[UID]
    __widget_attrs__: ClassVar[dict[str, WidgetAttr[Any]]]

    id: UID = WidgetAttr(init=False, default_factory=UID)

    superior: ContainerWidget = WidgetAttr(init=False)
    platform: Platform = WidgetAttr(init=False)
    native: NativeElement = WidgetAttr(init=False)

    dims: tuple[Pixels, Pixels] = WidgetAttr(init=False)
    pos: tuple[Pixels, Pixels] = WidgetAttr(init=False)
    abs_pos: tuple[Pixels, Pixels] = WidgetAttr(init=False)
    # --- runtime lint checks (ikik sorry, it's @TG-Techie on github) ---
    if __debug__ and not TYPE_CHECKING:

        def __new__(cls, *args, **kwargs):
            # widget classes must be decorated, _widget_cls_id_ is set if it is decorated
            if "__widget_class_id__" not in cls.__dict__:
                raise TypeError(
                    f"{cls} not decorated with @widget (or other widget decorator)"
                )

            if cls.__init__ is Widget.__init__ and len(args):
                raise TypeError(f"{cls} does not accept positional arguments")

            return object.__new__(cls)

    def __init_subclass__(cls) -> None:
        # check single inheritance
        assert 1 == len(
            overlap := set(filter(lambda base: issubclass(base, Widget), cls.__bases__))
        ), f"widgets cannot subclass multiple widgets types: {cls} inheriets from {overlap}"

        # check widget parent is first
        assert issubclass(
            cls.__bases__[0], Widget
        ), f"widget parent must be first base class: found {cls}'s first base class as {cls.__bases__[0]}"

    def _nest_in_(self, superior: ContainerWidget, platform: Platform) -> None:
        self._superior_ = superior
        self._platform_ = platform
        self.on_nest(platform)

    def _unnest_from_(self, superior: ContainerWidget, platform: Platform) -> None:
        assert (
            self._superior_ is superior
        ), f"{self} nested in {self._superior_}, cannot unnest from {superior}"
        assert self._platform_ is platform
        self.on_unnest(platform)
        # clear the vars
        self.superior = Missing  # type: ignore[assignment]
        self.platform = Missing  # type: ignore[assignment]

    def on_nest(self, platform: Platform) -> None:
        """
        Called when the widget is nested in a container widget.
        """

    def on_unnest(self, platform: Platform) -> None:
        """
        Called when the widget is unnested from a container widget.
        """

    @abstractmethod
    def _build_(self, suggestion: tuple[Pixels, Pixels]) -> None:
        """
        must set _dims_ and _native_ (as applicable)
        """
        raise NotImplementedError

    @abstractmethod
    def _demolish_(self) -> None:
        """
        must set _dims_ to None
        """
        raise NotImplementedError

    # TODO: add position specifiers
    @abstractmethod
    def _place_(self, position: tuple[Pixels, Pixels]) -> None:
        """
        must set _pos_ and _abs_pos_
        """
        raise NotImplementedError(f"{self}._place_({position})")

    @abstractmethod
    def _pickup_(self) -> None:
        """
        must set _pos_ and _abs_pos_ to None
        """
        raise NotImplementedError

    @abstractmethod
    def _show_(self) -> None:
        """
        must show the widget on the platform
        """
        raise NotImplementedError

    @abstractmethod
    def _hide_(self) -> None:
        """
        must hide the widget on the platform
        """
        raise NotImplementedError

    @classmethod
    def _iter_widgetcls_resolution(cls) -> Iterator[Type[Widget]]:
        # tg-gui-feature(future): use mro for theme resoultion once circuitpython supports it
        """
        iterate over the widget classes in the resolution order.
        This was implemented to replace .mro() on widget classes since it is not supported on circuitpython.
        ThemeAttrs use this to iterate over the widget classes so that (for instance)
        themed attrs for a Date would resolve before the Label (provided Date subclassed label).
        """
        curcls = cls.__bases__[0]
        while curcls is not Widget:
            assert issubclass(curcls, Widget), f"{curcls} is not a Widget, {curcls}"
            yield curcls
            curcls = curcls.__bases__[0]
        else:
            yield Widget

    @classmethod
    def _iter_widget_attrs(cls) -> Iterator[WidgetAttr[Any]]:
        return iter(cls.__widget_attrs__.values())
