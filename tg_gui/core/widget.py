from __future__ import annotations

from .implementation_support import (
    isoncircuitpython,
    class_id as _class_id,
    GenericABC,
)
from ._shared import uid, UID, Pixels, _Missing

from typing import TYPE_CHECKING, TypeVar, Generic, overload
from abc import ABC, abstractmethod, abstractproperty
from types import FunctionType
from enum import Enum, auto

_W = TypeVar("_W", bound="Widget")
_T = TypeVar("_T")

# circular and annotation-only imports
if TYPE_CHECKING:
    from ._shared import _Missing
    from typing import ClassVar, Type, Iterator, Callable, Any

    from .container_widget import ContainerWidget
    from .._platform_.platform import Platform, NativeElement, NativeContainer

_getname = lambda attr: attr._name_


def iswidgetclass(cls: type) -> bool:
    return (
        isinstance(cls, type)
        and issubclass(cls, Widget)
        and getattr(cls, "_widget_cls_id_", None) == _class_id(cls)
    )


def widget(cls):
    """
    This is a decotator for that all widgets need to be decorated with to apply sugar
    when asserts are on decoration is strictly enforced at runtime.
    TODO: add a better docstring
    !!DO NOT ADD TYPE ANNOTATIONS TO THIS FUNCTION (pylance)!!
    !!DO NOT ASSIGN TO THE `cls` LOCAL VARIABLE (pylance)!!
    """
    if TYPE_CHECKING:
        from dataclasses import dataclass

        return dataclass(
            init=True,
            repr=False,
            eq=False,
            order=False,
            unsafe_hash=False,
            frozen=False,
            match_args=False,
            kw_only=False,
            slots=False,
        )(cls)

    assert isinstance(cls, type) and issubclass(cls, Widget)

    clsid = _class_id(cls)

    # make sure widgets are single inheritance only
    # circuitpython-compat(__mro__) not supported
    assert 1 == len(
        overlap := set(
            basecls for basecls in cls.__bases__ if issubclass(basecls, Widget)
        )
    ), f"widgets cannot subclass multiple widgets types: {overlap}"

    # make sure the widget has not already been wrapped
    assert (
        "_widget_cls_id_" not in cls.__dict__
        and cls.__dict__.get("_widget_cls_id_", None) is not clsid
    ), f"{cls.__name__} already decorated with @widget (or other widget decorator)"

    # make sure it's first base is a Widget subclass
    assert issubclass(
        cls.__bases__[0], Widget
    ), f"{cls} must inherit from one Widget class as its first base class, found {cls.__bases__[0]}"

    # circuitpython does not support __set_name__ for descriptors, add it manually
    # circuitpython-compat(__set_name__) not supported
    if isoncircuitpython():
        for name, attr in cls.__dict__.items():
            if hasattr(attr, "__set_name__"):
                attr.__set_name__(cls, name)

    # tg-gui allows for classes to have a "._subclass_sugar_(...)" class method used
    # to format base classes after they have been wrapped.

    # climb up the inheritance tree and find the first Widget class and apply the subclass inits in the right order
    sugar_classes: list[Type[Widget]] = []
    for basecls in cls._iter_widgetcls_resolution():
        formatter = basecls.__dict__.get("_subclass_sugar_", None)
        if isinstance(formatter, (classmethod, staticmethod, FunctionType)):
            sugar_classes.append(basecls)
        # make sure it's not some other value
        else:
            assert formatter is None, (
                f"{basecls} has an invalid _subclass_sugar_ attribute ({FunctionType}). "
                + f"must be a classmethod or staticmethod, got {formatter}"
            )
    else:
        for basecls in reversed(sugar_classes):
            basecls._subclass_sugar_(cls)

    # parameters for the tg-gui widget classes are delcared using
    # buildattr and initattr descriptors. TO do this we pre-process the class attributes
    # and extract the parameters ahead of time.

    # create a flattened dict of the allowed init args
    # only add a dict if there are any new init args
    newkwargs: dict[str, InitAttr] = {
        name: attr for name, attr in cls.__dict__.items() if isinstance(attr, InitAttr)
    }
    # newer args of an existing arg replace the older ones
    if len(newkwargs):
        kwargs = cls._initkwargs_.copy()
        kwargs.update(newkwargs)
        cls._initkwargs_ = kwargs

    # make the class as a widget and set the unique id
    if __debug__:
        cls._widget_cls_id_ = clsid

    return cls


class Widget(ABC):

    _id_: UID

    _initkwargs_: ClassVar[dict[str, InitAttr]] = {}
    _subclass_sugar_: ClassVar[Callable[[Type[Widget]], None]]

    # --- nest phase ---
    _superior_: ContainerWidget = None  # type: ignore[assignment]
    _platform_: Platform = None  # type: ignore[assignment]

    # --- build phase ---
    _dims_: tuple[Pixels, Pixels] = None  # type: ignore[assignment]

    @abstractproperty
    def _native_(self) -> NativeElement | None:
        raise NotImplementedError

    # --- place phase ---
    _pos_: tuple[Pixels, Pixels] = None  # type: ignore[assignment]
    _abs_pos_: tuple[Pixels, Pixels] = None  # type: ignore[assignment]

    # --- runtime lint checks ---
    if __debug__ and not TYPE_CHECKING:

        def __new__(cls, *args, **kwargs):
            # widget classes must be decorated, _widget_cls_id_ is set if it is decorated
            if cls.__dict__.get("_widget_cls_id_", None) != _class_id(cls):
                raise TypeError(
                    f"{cls} not decorated with @widget (or other widget decorator)"
                )

            if cls.__init__ is Widget.__init__ and len(args):
                raise TypeError(f"{cls} does not accept positional arguments")

            return object.__new__(cls)

    def __init__(self, **kwargs):

        self._id_ = uid()

        # -- set attribute values ahead of time -
        # circuitpython requires all attributes to be reserved in __init__ otherwise
        # objects will be re-allocated more than necessary and run out of memory

        #  use none as not int placeholders as it should not be there
        # nest
        self._superior_ = None  # type: ignore[assignment]
        self._platform_ = None  # type: ignore[assignment]
        # build
        self._dims_ = None  # type: ignore[assignment]
        # place
        self._pos_ = None  # type: ignore[assignment]
        self._abs_pos_ = None  # type: ignore[assignment]

        # -- argument validation --
        # unexpected keyword arguments
        if len(extra := set(kwargs) - set(self._initkwargs_)):
            raise TypeError(
                f"{type(self).__name__}() got unexpected keyword argument(s): {'=, '.join(extra)}="
            )

        # missing required arguments
        missing = set()
        for name, attr in self._initkwargs_.items():
            if attr._required_ and name not in kwargs:
                missing.add(name)
            elif name in kwargs:
                attr._set_(self, kwargs[name])
        else:
            if len(missing):
                raise TypeError(
                    f"{type(self).__name__}() missing required keyword argument(s): {'=, '.join(missing)}="
                )

    def _get_init_args(
        self, kind: Type[InitAttr] | tuple[Type[InitAttr], ...]
    ) -> dict[str, Any]:
        return {
            name: getattr(self, name)
            for name, attr in self._initkwargs_.items()
            if isinstance(attr, kind)
        }

    def _is_nested(self) -> bool:
        assert (self._superior_ is None) == (self._platform_ is None)
        return self._superior_ is not None

    def _is_built(self) -> bool:
        return self._dims_ is not None

    def _is_placed(self) -> bool:
        assert (self._pos_ is None) == (self._abs_pos_ is None)
        return self._pos_ is not None

    def _nest_in_(self, superior: ContainerWidget, platform: Platform) -> None:
        assert not self._is_nested()
        self._superior_ = superior
        self._platform_ = platform
        self._on_nest_(superior, platform)

    def _unnest_from_(self, superior: ContainerWidget, platform: Platform) -> None:
        assert self._is_nested()
        assert (
            self._superior_ is superior
        ), f"{self} nested in {self._superior_}, cannot unnest from {superior}"
        assert self._platform_ is platform
        self._on_unnest_(superior, platform)
        self._superior_ = None  # type: ignore[assignment]
        self._platform_ = None  # type: ignore[assignment]

    @abstractmethod
    def _on_nest_(self, superior: ContainerWidget, platform: Platform) -> None:
        raise NotImplementedError

    @abstractmethod
    def _on_unnest_(self, superior: ContainerWidget, platform: Platform) -> None:
        raise NotImplementedError

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


_Self = TypeVar("_Self", bound="InitAttr")


class InitAttr(GenericABC[_T]):

    # TODO: add _build_proxy_ method to either throw error, return value, or bind to state

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

    @overload
    def __get__(self: _Self, owner: None, ownertype: Type[_W]) -> _Self:
        ...

    @overload
    def __get__(self, owner: _W, ownertype: Type[_W]) -> _T:
        ...

    def __get__(self, owner: None | _W, ownertype: Type[_W]) -> _T | InitAttr[_T]:
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


def buildattr(*, repr=False, private_name: str | None = None) -> BuildAttr:
    return BuildAttr(repr=repr, private_name=private_name)  # type: ignore


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
