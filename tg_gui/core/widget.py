from __future__ import annotations

from ._implementation_support_ import (
    isoncircuitpython,
    class_id as _class_id,
    GenericABC,
)
from ._shared_ import uid, UID, Pixels

from typing import TYPE_CHECKING, TypeVar, Generic
from abc import ABC, abstractmethod, abstractproperty
from types import FunctionType
from enum import Enum, auto

_T = TypeVar("_T")

# circular and annotation-only imports
if TYPE_CHECKING:
    from typing import ClassVar, Type, Iterator, Callable

    from .superior_widget import SuperiorWidget
    from .platform_widget import (
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

_getname = lambda attr: attr._name_


def widget(cls):
    """
    !!DO NOT ADD TYPE ANNOTATIONS TO THIS FUNCTION (pylance)!!
    !!DO NOT ASSIGN TO THE `cls` LOCAL VARIABLE (pylance)!!
    This is a decotator for that all widgets need to be decorated with to apply sugar
    when asserts are on decoration is strictly enforced at runtime.
    TODO: add better docstring
    """
    # if TYPE_CHECKING:
    #     return cls
    # else:
    #     assert isinstance(cls, type) and issubclass(cls, Widget)

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

    _apply_init_sugar(cls)

    if __debug__:
        cls._widget_cls_id_ = clsid

    return cls


def _apply_init_sugar(cls: Type[Widget]):
    # apply init sugar
    prevargs = cls._initargs_
    prevkwargs = cls._initkwargs_

    newargs: list[InitAttr] = []
    newkwargs: dict[str, InitAttr] = {}

    newattrs: list[tuple[str, InitAttr]] = sorted(
        filter(lambda item: isinstance(item[1], InitAttr), cls.__dict__.items()),
        key=lambda item: item[1]._id_,
    )
    prev = "<none>"
    for name, attr in newattrs:
        if name in prevkwargs:
            raise TypeError(
                f"init attribute {name} already defined in {cls.__bases__[0]}, overloading not supported (at least for now ?)"
            )
        if attr._positional_:
            if len(newkwargs):
                raise TypeError(
                    f"{cls} has positional init attribute .{name} after keyword init attribute .{prev}"
                )
            newargs.append(attr)

        assert (
            name not in newkwargs
        ), f"{name} already in new kwargs (within the same class body!?)"
        newkwargs[attr._name_] = attr

        prev = name

    # validate
    if len(newargs):
        cls._initargs_ = prevargs + tuple(newargs)

    # insert kwargs
    if len(newkwargs):
        kwargs = prevkwargs.copy()
        kwargs.update(newkwargs)
        cls._initkwargs_ = kwargs
        cls._initreqs_ = {name for name, attr in newattrs if attr._required_}


class Widget(ABC):

    _id_: UID

    _initargs_: ClassVar[tuple[InitAttr, ...]] = ()
    _initkwargs_: ClassVar[dict[str, InitAttr]] = {}
    _initreqs_: ClassVar[set[str]] = set()
    _subclass_sugar_: ClassVar[Callable[[Type[Widget]], None]]

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

    def __init__(self, *args, **kwargs):
        self._id_ = uid()
        # nest
        self._superior_ = None
        self._platform_ = None
        # build
        self._dims_ = None
        # place
        self._pos_ = None
        self._abs_pos_ = None

        cover_req_pos = []

        if len(args) > len(self._initargs_):
            raise TypeError(
                f"{type(self)} takes {len(self._initargs_)} positional arguments but {len(args)} were given"
            )

        for arg, attr in zip(args, self._initargs_):
            attr._set_(self, arg)
            if attr._required_:
                cover_req_pos.append(attr._name_)

        cover_req_kwargs = set()
        for name, attr in self._initkwargs_.items():
            if name in kwargs:
                assert (
                    name not in cover_req_pos
                ), f"{name} already covered by positional argument {cover_req_pos.index(name)}"
                attr._set_(self, kwargs[name])
                if attr._required_:
                    cover_req_kwargs.add(attr._name_)

        # if len(extra := set(kwargs) - set(self._initkwargs_)):
        #     raise TypeError(
        #         f"{type(self)} got an unexpected keyword argument(s) {', '.join(extra)}"
        #     )

        # if len(missing := set(self._initkwargs_) - set(kwargs)):
        #     raise TypeError(
        #         f"{type(self)} missing required keyword argument(s) {', '.join(missing)}"
        #     )

        # for attr_name, attr in self._initkwargs_.items():
        #     if attr_name in kwargs:
        #         attr._set_(self, kwargs[attr_name])

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
        """
        iterate over the widget classes in the resolution order
        """
        yield cls
        curcls = cls.__bases__[0]
        while curcls is not object:
            yield curcls
            curcls = curcls.__bases__[0]


class InitAttr(GenericABC[_T]):

    # --- public attributes ---
    _id_: UID
    _name_: str

    # --- abstract attributes ---
    _required_: bool
    _positional_: bool
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
        if owner is None:
            return self
        return self.get(owner)

    @abstractmethod
    def get(self, owner: Widget) -> _T:
        raise NotImplementedError

    @abstractmethod
    def _set_(self, owner: Widget, value: _T) -> None:
        raise NotImplementedError


# circuitpython compat(InitAttr.__class_getitem__) not supported, so we have to do this
if not TYPE_CHECKING and isoncircuitpython():
    _InitAttr = InitAttr
    InitAttr = {_T: _InitAttr}


class BuildAttr(InitAttr[_T]):

    _required_: bool = True
    _positional_: bool
    _build_: bool = True

    def __init__(
        self,
        *,
        positional: bool = False,
        repr: bool = False,
        private_name: str | None = None,
    ) -> None:
        self._positional_ = positional
        # self._override_ = override

        # if override and not positional:
        #     raise TypeError(f"{type(self)} overrides must be positional")

        super().__init__(repr=repr, private_name=private_name)

    def get(self, owner: Widget) -> _T:
        return getattr(owner, self._private_name)

    def _set_(self, owner: Widget, value: _T) -> None:
        setattr(owner, self._private_name, value)


# circuitpython compat(InitAttr.__class_getitem__) finish
if not TYPE_CHECKING and isoncircuitpython():
    InitAttr = _InitAttr
    del _InitAttr
