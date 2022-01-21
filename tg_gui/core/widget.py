from __future__ import annotations

from .implementation_support import (
    isoncircuitpython,
    class_id as _class_id,
    GenericABC,
)
from ._shared import uid, UID, Pixels, _Missing

from typing import TYPE_CHECKING, TypeVar, Generic
from abc import ABC, abstractmethod, abstractproperty
from types import FunctionType
from enum import Enum, auto

_T = TypeVar("_T")

# circular and annotation-only imports
if TYPE_CHECKING:
    from ._shared import _Missing
    from typing import ClassVar, Type, Iterator, Callable

    from .superior_widget import SuperiorWidget
    from .platform_widget import (
        Platform,
        NativeElement,
        NativeContainer,
    )

_getname = lambda attr: attr._name_


def buildattr(*, repr=False, private_name=None):
    return BuildAttr(repr=repr, private_name=private_name)


def widget(cls):
    """
    !!DO NOT ADD TYPE ANNOTATIONS TO THIS FUNCTION (pylance)!!
    !!DO NOT ASSIGN TO THE `cls` LOCAL VARIABLE (pylance)!!
    This is a decotator for that all widgets need to be decorated with to apply sugar
    when asserts are on decoration is strictly enforced at runtime.
    TODO: add better docstring
    """
    if TYPE_CHECKING:
        return cls

    assert isinstance(cls, type) and issubclass(cls, Widget)

    clsid = _class_id(cls)

    # circuitpython-compat(__mro__) not supported
    assert 1 == len(
        overlap := set(filter(lambda c: issubclass(c, Widget), cls.__bases__))
    ), f"widgets cannot subclass multiple widgets types: "

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

    # circuitpython does not support __set_name__ for descriptors, add it manually
    if isoncircuitpython():
        for name, attr in cls.__dict__.items():
            if hasattr(attr, "__set_name__"):
                attr.__set_name__(cls, name)

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

    # create a flattened dict of the allowed init args
    # only add a dict if there are any new init args
    newkwargs: dict[str, InitAttr] = {
        name: attr for name, attr in cls.__dict__.items() if isinstance(attr, InitAttr)
    }
    if len(newkwargs):
        kwargs = cls._initkwargs_.copy()
        kwargs.update(newkwargs)
        cls._initkwargs_ = kwargs

    if __debug__:
        cls._widget_cls_id_ = clsid

    return cls


class Widget(ABC):

    _id_: UID

    _initkwargs_: ClassVar[dict[str, InitAttr]] = {}
    _subclass_sugar_: ClassVar[Callable[[Type[Widget]], None]]

    # --- nest phase ---
    _superior_: SuperiorWidget | None = None
    _platform_: Platform | None = None

    # --- build phase ---
    _dims_: tuple[Pixels, Pixels] | None = None

    @abstractproperty
    def _native_(self) -> NativeElement | None:
        raise NotImplementedError

    # --- place phase ---
    _pos_: tuple[Pixels, Pixels] | None = None
    _abs_pos_: tuple[Pixels, Pixels] | None = None

    if __debug__ and not TYPE_CHECKING:

        def __new__(cls, *args, **kwargs):
            # widget classes must be decorated
            if cls.__dict__.get("_widget_cls_id_", None) != _class_id(cls):
                raise TypeError(
                    f"{cls} not decorated with @widgert (or other widget decorator)"
                )

            if cls.__init__ is Widget.__init__ and len(args):
                raise TypeError(f"{cls} does not accept positional arguments")

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

        if len(extra := set(kwargs) - set(self._initkwargs_)):
            raise TypeError(
                f"{type(self).__name__}() got an unexpected keyword argument(s): {'=, '.join(extra)}="
            )

        missing = set()
        for name, attr in self._initkwargs_.items():
            if attr._required_ and name not in kwargs:
                missing.add(name)
            elif name in kwargs:
                attr._set_(self, kwargs[name])

        if len(missing):
            raise TypeError(
                f"{type(self).__name__}() missing required keyword argument(s): {'=, '.join(missing)}="
            )

    if __debug__:

        def __repr__(self) -> str:
            attrdebug = ", ".join(
                f"{k}={repr(v.get(self))}"
                for k, v in self._initkwargs_.items()
                if v._repr
            )

            return f"<widget:{self._id_} {type(self).__name__}({attrdebug or '...'})>"

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


class InitAttr(GenericABC[_T]):

    # --- public attributes ---
    _id_: UID
    _name_: str

    # --- abstract attributes ---
    _required_: bool
    _build_: bool

    # --- private concrete attributes ---
    _private_name: str
    _repr: bool
    _owning_cls: Type[Widget]

    def __init__(
        self,
        *,
        repr: bool = False,
        private_name: str | None = None,
    ) -> None:
        self._id_ = uid()

        self._repr = repr

        # set in __set_name__
        self._name_ = None  # type: ignore[assignment]
        self._owning_cls = None  # type: ignore[assignment]
        self._private_name = private_name  # type: ignore[assignment]

    def __repr__(self) -> str:
        if self._name_ is None:
            return f"<{self.__class__.__name__}: {self._id_}>"
        else:
            return (
                f"<{type(self).__name__} "
                + f"{self._owning_cls.__module__}.{self._owning_cls.__name__}.{self._name_}>"
            )

    def __set_name__(self, cls: Type[Widget], name: str) -> None:
        assert self._name_ is None, f"{self} already set, cannot set again to {name}"
        assert self._owning_cls is None
        assert name.startswith("_") == name.endswith(
            "_"
        ), f"invalid {type(self).__name__} name {name}, cannot be private (ie if it starts with _ it must end with _)"

        self._name_ = name
        self._owning_cls = cls
        if not self._private_name:
            self._private_name = f"_{name if __debug__ else ''}_{self._id_}"

        assert (
            name != self._private_name
        ), f"{name} is the same as the private name in __set_name__"

    def __get__(self, owner: Widget, ownertype: Type[Widget]) -> _T:
        assert self._name_ is not None, f"{self} not initialized with __set_name__"
        # circuitpython-compat(__get__)
        if owner is None:
            return self  # type: ignore[return-value]
        return self.get(owner)

    @abstractmethod
    def get(self, owner: Widget) -> _T:
        raise NotImplementedError

    @abstractmethod
    def _set_(self, owner: Widget, value: _T) -> None:
        raise NotImplementedError


# circuitpython-compat(__class_getitem__) not supported, so we have to do this
if not TYPE_CHECKING and isoncircuitpython():
    _InitAttr = InitAttr
    InitAttr = {_T: _InitAttr}


class BuildAttr(InitAttr[_T]):

    _required_: bool = True
    _build_: bool = True

    def get(self, owner: Widget) -> _T:
        return getattr(owner, self._private_name)

    def _set_(self, owner: Widget, value: _T) -> None:
        setattr(owner, self._private_name, value)


# circuitpython-compat(__class_getitem__) finish
if not TYPE_CHECKING and isoncircuitpython():
    InitAttr = _InitAttr
    del _InitAttr
