from __future__ import annotations


from typing import TYPE_CHECKING, TypeVar


if TYPE_CHECKING:
    from typing import ClassVar, Type, Iterator, Any, Literal

    # from typing_extensions import Self
    from tg_gui.platform import Platform, NativeElement
    from .container import ContainerWidget


# ---

from abc import ABC, abstractmethod

from .shared import UID, Pixels, add_pixel_pair as _add_pixel_pair
from .attrs import WidgetAttr, widget
from .implementation_support import Missing, isoncircuitpython


## subclasses require the @widget decorator
# @widget
class Widget(ABC):
    if TYPE_CHECKING:
        Self = TypeVar("Self", bound="Widget", contravariant=True)

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

    # -------- subclass specific methods --------
    def on_nest(self, platform: Platform) -> None:
        """
        Called when the widget is nested in a container widget.
        """
        pass

    def on_unnest(self, platform: Platform) -> None:
        """
        Called when the widget is unnested from a container widget.
        """
        pass

    @abstractmethod
    def build(
        self: Self, suggestion: tuple[Pixels, Pixels]
    ) -> tuple[NativeElement, tuple[Pixels, Pixels]]:
        """
        builds a native element that is the concrete implementation of the
        widget based on the suggested size.
        In this method, subclasses of Widget must:
        - assign self.native to the native element that corresponds to that subclass
        - assign self.dims based on the size of the native element
        """
        raise NotImplementedError

    # -------- internal methods --------
    def _nest_in_(self, superior: ContainerWidget, platform: Platform) -> None:
        """
        internal method to nest a widget in a container widget.
        """
        self._superior_ = superior
        self._platform_ = platform
        self.on_nest(platform)

    def _unnest_from_(self, superior: ContainerWidget, platform: Platform) -> None:
        """
        internal method to unnest a widget from a container widget.
        """
        assert (
            self._superior_ is superior
        ), f"{self} nested in {self._superior_}, cannot unnest from {superior}"
        assert self._platform_ is platform
        self.on_unnest(platform)
        # clear the .superior and .platform attributes using a hidden WidgetAttr method
        self.superior = Missing  # type: ignore[assignment]
        self.platform = Missing  # type: ignore[assignment]

    def _build_(self, suggestion: tuple[Pixels, Pixels]) -> None:
        """
        Called when the widget is created.
        """
        self.native, self.dims = self.build(suggestion)

    def _place_(self, pos: tuple[Pixels, Pixels]) -> None:
        """
        Called when the widget is placed in its container.
        """
        self.pos = pos
        self.abs_pos = _add_pixel_pair(self.superior.abs_pos, self.pos)

    # @abstractmethod
    # def _build_(self, suggestion: tuple[Pixels, Pixels]) -> None:
    #     """
    #     must set _dims_ and _native_ (as applicable)
    #     """
    #     raise NotImplementedError

    # @abstractmethod
    # def _demolish_(self) -> None:
    #     """
    #     must set _dims_ to None
    #     """
    #     raise NotImplementedError

    # # TODO: add position specifiers
    # @abstractmethod
    # def _place_(self, position: tuple[Pixels, Pixels]) -> None:
    #     """
    #     must set _pos_ and _abs_pos_
    #     """
    #     raise NotImplementedError(f"{self}._place_({position})")

    # @abstractmethod
    # def _pickup_(self) -> None:
    #     """
    #     must set _pos_ and _abs_pos_ to None
    #     """
    #     raise NotImplementedError

    # @abstractmethod
    # def _show_(self) -> None:
    #     """
    #     must show the widget on the platform
    #     """
    #     raise NotImplementedError

    # @abstractmethod
    # def _hide_(self) -> None:
    #     """
    #     must hide the widget on the platform
    #     """
    #     raise NotImplementedError

    def __init_subclass__(cls) -> None:
        """
        Use this to enfoce single inheritance for widget classes.
        """

        # check single inheritance
        assert 1 == len(
            overlap := set(
                filter(
                    lambda base: issubclass(base, Widget),
                    cls.__bases__,
                )
            )
        ), f"widgets cannot subclass multiple widgets types: {cls} inheriets from {overlap}"

        # check widget parent is first
        assert issubclass(
            cls.__bases__[0], Widget
        ), f"widget parent must be first base class: found {cls}'s first base class as {cls.__bases__[0]}"

    if not TYPE_CHECKING:
        # the init implementation is the same for all widget classes,
        # however a specific widget subclass may override it
        from .attrs import _widget_decorator__init__inject as __init__

    # --- runtime lint checks (ikik sorry, @TG-Techie on github) ---
    if __debug__ and not TYPE_CHECKING:

        def __new__(cls, *args, **kwargs):
            # widget classes must be decorated, _widget_cls_id_ is set if it is decorated
            if "__widget_class_id__" not in cls.__dict__:
                raise TypeError(
                    f"{cls} not decorated with some @widget decorator or "
                    "other class initialization error occurred (maybe __init_subclass__? etc)"
                )

            if cls.__init__ is Widget.__init__ and len(args):
                raise TypeError(f"{cls} does not accept positional arguments")

            return object.__new__(cls)
