from __future__ import annotations

from ._implementation_support_ import (
    enum_compat,
    class_id as _class_id,
    isoncircuitpython,
)
from ._shared_ import uid, UID, Pixels

from enum import Enum, auto
from typing import TYPE_CHECKING, TypeVar, Generic
from types import FunctionType
from abc import ABC, abstractmethod, abstractproperty

_T = TypeVar("_T")

# circular and annotation-only imports
if TYPE_CHECKING:
    from typing import ClassVar, Type, Iterator, overload, Literal

    from .superior_widget import SuperiorWidget
    from .platform_widget import (
        PlatformWidget,
        Platform,
        NativeElement,
        NativeContainer,
    )

if TYPE_CHECKING or not isoncircuitpython():

    class _MissingType(Enum):
        missing = auto()

    _Missing = _MissingType.missing
else:
    _Missing = type("MissingType", (), {})() if __debug__ or TYPE_CHECKING else object()


def widget(cls):
    """
    !!DO NOT ADD TYPE ANNOTATIONS TO THIS FUNCTION!!
    This is a decotator for that all widgets need to be decorated with to apply sugar
    when asserts are on decoration is strictly enforced at runtime.
    TODO: add better docstring
    """
    if TYPE_CHECKING:
        return cls
    else:
        assert isinstance(cls, type) and issubclass(cls, Widget)

    clsid = _class_id(cls)

    assert (
        "_widget_cls_id_" not in cls.__dict__
        and cls.__dict__.get("_widget_cls_id_", None) is not clsid
    ), f"{cls.__name__} already decorated with @widget (or other widget decorator)"

    assert 1 == sum(
        issubclass(basecls, Widget) for basecls in cls.__bases__
    ), f"{cls} must inherit from one Widget class"
    assert issubclass(
        cls.__bases__[0], Widget
    ), f"{cls} must inherit from one Widget class"

    cls: Type[Widget]

    # climb up the inheritance tree and find the first Widget class and apply the subclass inits in the right order
    sugar_classes: list[Type[Widget]] = []
    for basecls in cls._iter_widgetcls_resolution():
        formatter = basecls.__dict__.get("_subclass_sugar_", None)
        if isinstance(formatter, (classmethod, staticmethod, FunctionType)):
            sugar_classes.append(basecls)
        else:
            assert formatter is None, (
                f"{basecls} has an invalid _subclass_sugar_ attribute ({FunctionType}). "
                + "must be a classmethod or staticmethod"
            )

    for basecls in reversed(sugar_classes):
        basecls._subclass_sugar_(cls)

    # circuitpython does not support __set_name__ for descriptors, add it manually
    if isoncircuitpython():
        for name, attr in cls.__dict__.items():
            if hasattr(attr, "__set_name__"):
                attr.__set_name__(cls, name)

    if __debug__:
        cls._widget_cls_id_ = clsid

    return cls


class Widget(ABC):

    _id_: UID

    _initattrs_: ClassVar[dict[str, InitAttr]] = {}

    # --- nest phase ---
    _superior_: SuperiorWidget | None = None
    _platform_: Platform | None = None

    # --- build phase ---
    _dims_: tuple[Pixels, Pixels] | None = None

    @abstractproperty
    def _native_(self) -> NativeElement | None:
        raise NotImplementedError

    @_native_.setter
    def _native_(self, native: NativeElement | None) -> None:
        raise NotImplementedError

    # --- place phase ---
    _pos_: tuple[Pixels, Pixels] | None = None
    _abs_pos_: tuple[Pixels, Pixels] | None = None

    if __debug__:

        def __new__(cls, *args, **kwargs):
            # widget classes must be decorated
            assert cls.__dict__.get("_widget_cls_id_", None) == _class_id(
                cls
            ), f"{cls} not decorated with @widgert (or other widget decorator)"
            return object.__new__(cls)

    def __init__(self, **kwargs):
        self._id_ = uid()
        # nest
        self._superior_ = None
        self._platform_ = None
        # build
        self._dims_ = None
        # place
        self._pos_ = None
        self._abs_pos_ = None

        if len(extra := set(kwargs) - set(self._initattrs_)):
            raise TypeError(
                f"{type(self)} got an unexpected keyword argument(s) {', '.join(extra)}"
            )

        if len(missing := set(self._initattrs_) - set(kwargs)):
            raise TypeError(
                f"{type(self)} missing required keyword argument(s) {', '.join(missing)}"
            )

        for attr_name, attr in self._initattrs_.items():
            if attr_name in kwargs:
                attr._set(self, kwargs[attr_name])

    if __debug__:

        def __repr__(self) -> str:
            attrdebug = ", ".join(
                f"{k}={repr(v.get(self))}"
                for k, v in self._initattrs_.items()
                if v._repr
            )
            # append space if there is any repr into
            attrdebug = " " + attrdebug if attrdebug else ""
            return f"<{type(self).__name__}: {self._id_}{attrdebug}>"

    else:

        def __repr__(self) -> str:
            return f"<{type(self).__name__}: {self._id_}>"

    if __debug__:

        def _is_nested(self) -> bool:
            assert (self._superior_ is None) == (self._platform_ is None)
            return self._superior_ is not None

        def _is_built(self) -> bool:
            return self._dims_ is not None

        def _is_placed(self) -> bool:
            assert (self._pos_ is None) == (self._abs_pos_ is None)
            return self._pos_ is not None

    def _nest_in_(self, superior: SuperiorWidget, platform: Platform) -> None:
        assert not self._is_nested()
        self._superior_ = superior
        self._platform_ = platform

    def _unnest_from_(self, superior: SuperiorWidget, platform: Platform) -> None:
        assert self._is_nested()
        assert (
            self._superior_ is superior
        ), f"{self} nested in {self._superior_}, cannot unnest from {superior}"
        assert self._platform_ is platform
        self._superior_ = None
        self._platform_ = None

    @abstractmethod
    def _build_(self, suggestion: tuple[Pixels, Pixels]) -> None:
        """
        must set _dims_
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
        raise NotImplementedError

    @abstractmethod
    def _pickup_(self) -> None:
        """
        must set _pos_ and _abs_pos_ to None
        """
        raise NotImplementedError

    @classmethod
    def _iter_widgetcls_resolution(cls) -> Iterator[Type[Widget]]:
        """
        iterate over the widget classes in the resolution order
        """
        yield cls
        curcls = cls.__bases__[0]
        while curcls is not object:
            yield curcls
            curcls = curcls.__bases__[0]

    @staticmethod
    def _subclass_sugar_(subcls: Type[Widget]) -> None:
        # TODO: on cpython add
        # if there are new init arguments, make a new dict and set it as a class attribute
        # if there are no new ones, do not set the class attribute
        newattrs = {
            name: attr
            for name, attr in subcls.__dict__.items()
            if isinstance(attr, InitAttr)
        }
        if len(newattrs):
            attrs = dict(subcls._initattrs_)
            attrs.update(newattrs)
            subcls._initattrs_ = attrs


class InitAttr(Generic[_T]):

    _id_: UID
    name: str

    _private_name: str
    _repr: bool
    _owning_cls: Type[Widget]

    def __init__(self, repr: bool = False, private_name: str | None = None) -> None:
        self._id_ = uid()

        self._repr = repr

        # set in __set_name__
        self.name = None  # type: ignore[assignment]
        self._owning_cls = None  # type: ignore[assignment]
        self._private_name = private_name  # type: ignore[assignment]\

    def __repr__(self) -> str:
        if self.name is None:
            return f"<{self.__class__.__name__}: {self._id_}>"
        else:
            return (
                f"<{type(self).__name__} "
                + f"{self._owning_cls.__module__}.{self._owning_cls.__name__}.{self.name}>"
            )

    def __set_name__(self, cls: Type[Widget], name: str) -> None:
        assert self.name is None
        assert self._owning_cls is None
        assert name.startswith("_") == name.endswith(
            "_"
        ), f"invalid {type(self).__name__} name {name}, cannot be private (ie if it starts with _ it must end with _)"

        self.name = name
        self._owning_cls = cls
        if not self._private_name:
            self._private_name = f"_{name if __debug__ else ''}_{self._id_}"

    def __get__(self, owner: Widget, ownertype: Type[Widget]) -> _T:
        assert self.name is not None, f"{self} not initialized with __set_name__"
        if owner is None:
            return self
        return self.get(owner)

    def get(self, owner: Widget) -> _T:
        return getattr(owner, self._private_name)

    def _set(self, owner: Widget, value: _T) -> None:
        setattr(owner, self._private_name, value)
