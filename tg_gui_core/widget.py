from __future__ import annotations


from typing import TYPE_CHECKING, TypeVar


if TYPE_CHECKING:
    from typing import ClassVar, Type, Iterator, Any, Literal

    # from typing_extensions import _Self
    from tg_gui.platform.shared import Platform, NativeElement, NativeContainer
    from .container import ContainerWidget


# ---

from abc import ABC, abstractmethod

from .shared import UID, Pixels, add_pixel_pair as _add_pixel_pair
from .attrs import WidgetAttr, widget
from .implementation_support import Missing, isoncircuitpython


## subclasses require the @widget decorator
@widget
class Widget(ABC):
    # if TYPE_CHECKING:
    #     _Self = TypeVar("_Self", bound="Widget", contravariant=True)

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

    # set the init method, it is defined in .attrs b/c more info there is related
    if not TYPE_CHECKING:
        from .attrs import _widget_decorator__init__inject as __init__

    # -------- public, override-able methods --------
    def on_nest(self) -> None:
        """
        Called when the widget is nested in a container widget.
        """
        pass

    def on_unnest(self) -> None:
        """
        Called when the widget is unnested from a container widget.
        """
        pass

    # ------- internal methods -------

    def nest_in(self, superior: ContainerWidget, platform: Platform) -> None:
        """
        internal method to nest a widget in a container widget.
        """
        self._superior_ = superior
        self._platform_ = platform
        self.on_nest()

    def unnest_from(self, superior: ContainerWidget, platform: Platform) -> None:
        """
        internal method to unnest a widget from a container widget.
        """
        assert (
            self._superior_ is superior
        ), f"{self} nested in {self._superior_}, cannot unnest from {superior}"
        assert self._platform_ is platform
        self.on_unnest()
        # clear the .superior and .platform attributes using a hidden WidgetAttr method
        # self.superior = Missing  # type: ignore[assignment]
        self.platform = Missing  # type: ignore[assignment]

    def build(self, suggestion: tuple[Pixels, Pixels]) -> None:
        """
        Called when the widget is created.
        """
        self.native, self.dims = self._build_(suggestion)

    def demolish(self) -> None:
        """
        Called when the widget is destroyed.
        """
        native = self.native
        self.native = Missing  # clear the superior and platform attributes using a hidden WidgetAttr method
        self._demolish_(native)

    def place(self, pos: tuple[Pixels, Pixels]) -> None:
        """
        Called when the widget is placed in its container.
        WARNING: this method only stores the position, it does not set the
        position of the native element in it's conainer. That is the responsibility of the
        the widget's superior
        """
        self.pos = pos
        self.abs_pos = abs_pos = _add_pixel_pair(self.superior.abs_pos, pos)
        self._place_(self.superior.native, (self.native), self.pos, abs_pos)

    def pickup(self) -> None:
        """
        Called when removing the widget from a container.
        """
        self._pickup_(self.superior.native, self.native)

    def rebuild(self, suggestion: tuple[Pixels, Pixels]) -> None:
        """
        Rebuilds the widget.
        """
        self.native, self.dims = self._rebuild_(self.native, suggestion)

    def move(self, pos: tuple[Pixels, Pixels]) -> None:
        """
        Moves the widget by the given amount.
        """
        self._move_(
            self.superior.native,
            self.native,
            pos,
            _add_pixel_pair(self.superior.abs_pos, pos),
        )

    # ---- internal methods required by the a platform to suppy support ----

    # --- build / demolish ---
    @abstractmethod
    def _build_(
        self, suggestion: tuple[Pixels, Pixels]
    ) -> tuple[NativeElement, tuple[Pixels, Pixels]]:
        """
        builds a native element that is the concrete implementation of the
        widget based on the suggested size.
        This may be responsible for nesting the native element in the native container.
        :return: a tuple of the native element and the size final size of the widget
        """
        raise NotImplementedError

    @abstractmethod
    def _demolish_(self, native: NativeElement) -> None:
        """
        demolishes the widget's native element.
        This may be responsible for nesting the native element in the native container.
        Must undo the actions of the build method.
        """
        raise NotImplementedError

    # --- place / unplace ---
    @abstractmethod
    def _place_(
        self,
        container: NativeContainer,
        native: NativeElement,
        pos: tuple[Pixels, Pixels],
        abs_pos: tuple[Pixels, Pixels],
    ) -> None:
        """
        Places the widget in given one of the coordinates.
        This may be responsible for nesting the native element in the native container.
        """
        raise NotImplementedError

    @abstractmethod
    def _pickup_(
        self,
        container: NativeContainer,
        native: NativeElement,
    ) -> None:
        """
        Called when the widget is picked up by the platform.
        This may be responsible for un-nesting the native element from the native container.
        Must undo the actions of the place method.
        """
        raise NotImplementedError

    # --- re-layout / utilites ---
    # both can/should be overridden by subclasses to provide more efficient implementations
    def _rebuild_(
        self, native: NativeElement, suggestion: tuple[Pixels, Pixels]
    ) -> tuple[NativeElement, tuple[Pixels, Pixels]]:
        """
        Called when the widget is resized.
        This is a default implementation that calls the build method. Specific widgets
        can override this method to perform a more efficient rebuild.
        :param native: the native element that should be rebuilt or modified
        :param suggestion: the suggested size of the new native element
        :return: the new native element and the size of the new native element
        """
        self._demolish_(native)
        return self._build_(suggestion)

    def _move_(
        self,
        container: NativeContainer,
        native: NativeElement,
        pos: tuple[Pixels, Pixels],
        abs_pos: tuple[Pixels, Pixels],
    ) -> None:
        """
        Moves the widget by the given amount.
        This is a default implementation that calls the place method. Specific widgets
        can override this method to perform a more efficient move.
        """
        self._pickup_(container, native)
        self._place_(container, native, pos, abs_pos)

    # --- widget subclassing / etc related methods ---

    def __init_subclass__(cls) -> None:  # pyright: reportMissingSuperCall=false
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
