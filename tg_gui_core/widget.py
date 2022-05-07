from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar


if TYPE_CHECKING:
    from typing import ClassVar, Type, Iterator, Any
    from typing_extensions import Self
    from tg_gui.platform import Platform, NativeElement
    from .container import ContainerWidget
# ---

from abc import ABC, abstractmethod

from .shared import UID, Pixels
from .attrs import WidgetAttr, ReservedAttr
from .implementation_support import Missing, isoncircuitpython

if TYPE_CHECKING:
    _W = TypeVar("_W", bound="Widget")

    def widget(cls: Type[_W]) -> Type[_W]:
        return cls


## subclasses require the @widget decorator
class Widget(ABC):
    id: UID
    __widget_class_id__: ClassVar[UID]
    __widget_attrs__: dict[str, WidgetAttr[Any]] = {}

    superior: ReservedAttr[ContainerWidget] = ReservedAttr()
    platform: ReservedAttr[Platform] = ReservedAttr()
    native: ReservedAttr[NativeElement] = ReservedAttr()

    dims: ReservedAttr[tuple[Pixels, Pixels]] = ReservedAttr()
    pos: ReservedAttr[tuple[Pixels, Pixels]] = ReservedAttr()
    abs_pos: ReservedAttr[tuple[Pixels, Pixels]] = ReservedAttr()
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

    def __init__(self, **kwargs: object):

        self._id_ = UID()

        # init the widget attrs, this may reserve space fetch from the kwargs, etc
        for attr in self._iter_widget_attrs():
            init_value = kwargs.pop(attr.name, Missing) if attr.in_init else Missing

            if attr.init_required and init_value is Missing:
                raise TypeError(
                    f"{self.__class__.__name__}.__init__(...) "
                    + f"missing required argument '{attr.name}'"
                )
            else:
                attr.init(self, init_value)

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
        self.superior = Missing
        self.platform = Missing

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


# ... below
if not TYPE_CHECKING:

    def widget(cls: Type[Widget]):
        """
        Decorator for widget classes that performs the following:
        - circuitpython-compat(__set_name__), call `__set_name__` for the attributes in the class
        - validates widgets use only single inheritance for widget base classes
        - validate it's parent widget class is in it's first position
        - sets the widget class id (runtime id)
        - setup the widget attrs if included in `__init__` signature
        """

        # check single inheritance
        assert 1 == len(
            overlap := set(filter(lambda base: issubclass(base, Widget), cls.__bases__))
        ), f"widgets cannot subclass multiple widgets types: {cls} inheriets from {overlap}"

        # check widget parent is first
        assert issubclass(
            cls.__bases__[0], Widget
        ), f"widget parent must be first base class: found {cls}'s first base class as {cls.__bases__[0]}"

        # set an id for the widget class, unless it already has one
        assert (
            "__widget_class_id__" not in cls.__dict__
        ), f"widget class {cls} already has a class id, make sure it is not decorated with `@widget` twice"
        cls.__widget_class_id__ = UID()

        # circuitpython-compat(__set_name__)
        if isoncircuitpython():
            for name, attr in cls.__dict__.items():
                if hasattr(attr, "__set_name__"):
                    attr.__set_name__(cls, name)

        # stash widget_attrs
        widget_attrs: dict[str, WidgetAttr[Any]] = {
            k: v for k, v in cls.__dict__.items() if isinstance(v, WidgetAttr)
        }
        # if there are new init attrs, make a new dict based on the old one
        # and override the old init attrs
        if len(widget_attrs):
            assert hasattr(
                cls, "__widget_attrs__"
            ), f"internal error: widget {cls} has no __widget_attrs__, this should never be the case"
            init_attrs = getattr(cls, "__widget_attrs__").copy()
            init_attrs.update(widget_attrs)
            cls.__widget_attrs__ = init_attrs

        return cls
