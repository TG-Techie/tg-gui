from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from typing import Callable, overload, Type, Any, Literal, overload, Union
    from typing_extensions import Self
    from .widget import Widget

    _WidgetAttrDefaultSource = Union[
        tuple[Literal["required"], None],
        tuple[Literal["default"], Any],
        tuple[Literal["default_factory"], Callable[[], Any]],
    ]

# ---

from enum import Enum, auto

from .shared import UID, Missing, MissingType, idattr
from . import implementation_support as impl_support


_Attr = TypeVar("_Attr")
_W = TypeVar("_W", bound="Widget")


@impl_support.generic_compat
class WidgetAttr(Generic[_Attr]):
    # NOTE: __new__ defined at the bottom of this class

    # -- widget runtime related --
    build: bool
    style: bool

    # -- init usage related --
    init: bool
    kw_only: bool
    default_source: _WidgetAttrDefaultSource
    # default: _Attr | MissingType = Missing
    # default_factory: Callable[[], _Attr] | MissingType = Missing

    # -- info --
    id: UID
    name: str
    owning_cls: type
    private_name: str

    def init_attr(self, widget: Widget, value: _Attr | MissingType) -> None:
        """
        Called when the widget is being initialized, this can be used to reserve the attribute
        for later use, performing any necessary initialization, etc.
        :param widget: the widget being initialized
        :param value: the value passed to the init of called widget class,
            ex then in `w = SomeWidget(foo=bar))` is like calling `SomeWidget.foo.init_attr(w, bar)`
        """
        setattr(widget, self.private_name, value)

    def get_attr(self, owner: Widget) -> _Attr:
        """
        Called when the widget is being accessed, find and return the value of the attribute this widgetattr describes.
        :param owner: the widget being accessed
        """
        attr: _Attr | MissingType = getattr(self, self.private_name, Missing)
        if attr is Missing:
            raise AttributeError(
                f"{self} has not attribute `.{self.name}`, "
                "either uninited or cleared"
            )
        else:
            return attr

    def set_attr(self, widget: Widget, value: _Attr | MissingType = Missing) -> None:
        """
        Called when the attribute on the widget is being set, ex:
        ```
        @widget
        class Foo(Widget):
            x = WidgetAttr(init=True)

        f = Foo()
        f.x = 10 # calls Foo.x.set_attr(f, 10)
        ```
        """
        raise AttributeError(
            f"{self.name} is a read-only attribute, tried to set to {value} on {widget}"
        )

    if TYPE_CHECKING:

        @overload
        def __get__(self, widget: None, ownertype: Type[Widget]) -> Self:
            ...

        @overload
        def __get__(self, widget: Widget, ownertype: Type[Widget]) -> _Attr:
            ...

    def __get__(self, widget: Widget | None, ownertype: Type[Widget]) -> _Attr | Self:
        if widget is None:
            return self

        value = self.get_attr(widget)

        if value is Missing:
            raise AttributeError(f"{self.name} cleared or not set, cannot be accessed")

        return value

    def __set__(self, widget: Widget, value: _Attr | MissingType = Missing) -> None:
        return self.set_attr(widget, value)

    def __set_name__(self, cls: Type[Widget], name: str) -> None:
        assert (
            getattr(self, "name", None) is None
        ), f"{self} already set, cannot set again to {name}"
        assert getattr(self, "owning_cls", None) is None

        assert name.startswith("_") == name.endswith(
            "_"
        ), f"invalid {type(self).__name__} name {name}, cannot be private (ie if it starts with _ it must end with _)"

        self.name = name
        self.owning_cls = cls
        if not getattr(self, "private_name", None):
            self.private_name = f"_{name if __debug__ else self.id}"

        assert (
            name != self.private_name
        ), f"{name} is the same as the private name in __set_name__"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}:{self.id} `{self.owning_cls.__qualname__}.{self.name}`>"

    # NOTE: this uses, the yet to be approved, pep 681
    # https://peps.python.org/pep-0681/#field-specifiers
    # make sure the return type of `__new__` is `Any`, pyright infers the type of the attribute
    #    ```
    #    @widget
    #    class Foo(View):
    #        counter: int | None = State(default=None)
    #    ```
    if TYPE_CHECKING:

        @overload
        def __new__(
            cls: type[Self],
            *,
            init: Literal[False],
            build: bool = False,
            style: bool = False,
        ) -> Any | _Attr:
            ...

        @overload
        def __new__(
            cls: type[Self],
            *,
            init: Literal[True],
            kw_only: bool = True,
            # TODO: add repr=:bool = False, # when init is True
            build: bool = False,
            style: bool = False,
        ) -> Any | _Attr:
            ...

        @overload
        def __new__(
            cls: type[Self],
            *,
            default: _Attr,
            init: Literal[False],
            build: bool = False,
            style: bool = False,
        ) -> Any | _Attr:
            ...

        @overload
        def __new__(
            cls: type[Self],
            *,
            default: _Attr,
            init: Literal[True],
            kw_only: bool = True,
            build: bool = False,
            style: bool = False,
        ) -> Any | _Attr:
            ...

        @overload
        def __new__(
            cls: type[Self],
            *,
            default_factory: Callable[[], _Attr],
            init: Literal[False],
            build: bool = False,
            style: bool = False,
        ) -> Any | _Attr:
            ...

        @overload
        def __new__(
            cls: type[Self],
            *,
            default_factory: Callable[[], _Attr],
            init: Literal[True],
            kw_only: bool = True,
            build: bool = False,
            style: bool = False,
        ) -> Any | _Attr:
            ...

        def __new__(cls: type[Self], *_, **__):
            ...


# ----------- decorator -----------

if TYPE_CHECKING:
    # NOTE: this uses, the yet to be approved, pep 681
    from typing_extensions import dataclass_transform

    _W = TypeVar("_W", bound="Widget")

    @dataclass_transform(
        # all widget attrs are
        kw_only_default=True,
        field_descriptors=(WidgetAttr,),
        eq_default=False,  # widgets are never equatable
        order_default=False,  # widgets are not ordered...
    )
    def widget(cls: Type[_W]) -> Type[_W]:
        return cls

else:

    def widget(cls: Type[Widget]) -> Type[Widget]:
        return _widget(cls)


# ----------- decorator impl -----------


def _widget(cls: Type[_W]) -> Type[_W]:
    """
    Decorator for widget classes that performs the following:
    - circuitpython-compat(__set_name__), call `__set_name__` for the attributes in the class
    - circuitpython-compat(__init_subclass__), a limited version of `__init_subclass__` without kwargs
    - validates widgets use only single inheritance for widget base classes
    - validate it's parent widget class is in it's first position
    - sets the widget class id (runtime id)
    - setup the widget attrs if included in `__init__` signature
    """
    # check this is a widget class
    assert (
        getattr(cls, "__is_widget_class__", None) is True
    ), f"{cls} does not subclass Widget"

    # circuitpython-compat(__init_subclass__), does not support **kwargs
    if hasattr(super(cls, cls), "__init_subclass__"):
        super(cls, cls).__init_subclass__()  # type: ignore[attr-defined]

    # set an id for the widget class, unless it already has one
    assert (
        "__widget_class_id__" not in cls.__dict__
    ), f"widget class {cls} already has a class id, make sure it is not decorated with `@widget` twice"
    cls.__widget_class_id__ = UID()

    # circuitpython-compat(__set_name__)
    if impl_support.isoncircuitpython():
        for name, attr in cls.__dict__.items():
            if hasattr(attr, "__set_name__"):
                attr.__set_name__(cls, name)

    # --- setup the argument and inst attrs ---
    # inject the init that will parse and apply the arguemtn parsing that @widget proivides
    assert "__init__" not in cls.__dict__, f"{cls} must have an __init__ method"
    cls.__init__ = _widget_decorator__init__inject  # type: ignore[assignment]

    assert (
        "__widget_attrs__" not in cls.__dict__
    ), f"{cls} already has a '__widget_attrs__' .__dict__ entry"
    widget_attrs: dict[str, WidgetAttr[Any]] = {
        k: v for k, v in cls.__dict__.items() if isinstance(v, WidgetAttr)
    }
    # if there are new init attrs, make a new dict based on the old one
    # and override the old init attrs
    if len(widget_attrs):
        # assert hasattr(
        #     cls, "__widget_attrs__"
        # ), f"internal error: widget {cls} has no __widget_attrs__, this should never be the case"

        init_attrs = getattr(cls, "__widget_attrs__", {}).copy()
        init_attrs.update(widget_attrs)
        cls.__widget_attrs__ = init_attrs

    return cls


def _widget_decorator__init__inject(
    self: Widget,
    *args,
    **kwargs: object,
) -> None:

    init_attrs = self.__widget_attrs__.copy()

    # --- positional args ---
    # find which positional args are init attrs, sort by order by id (childmost -> parentmost, top -> down)
    pos_args = sorted(
        filter(lambda wa: wa.init and not wa.kw_only, init_attrs.values()), key=idattr
    )
    # number of function arguments
    if not (len(args) <= len(pos_args)):
        TypeError(
            f"{self.__class__}.__init__(...) expected {len(pos_args)} positional args, but {len(args)} were passed"
        )
    # match positional args and remove them from the remaining kwargs
    for arg, wa in zip(args, pos_args):
        if not (wa.name not in kwargs):
            TypeError(
                f"{self.__class__}.__init__(...) got multiple values for {wa.name}="
            )
        wa.init_attr(self, arg)
        init_attrs.pop(wa.name)

    # --- keyword and deafult args ---
    # go through all the remaining kwargs and set the init attrs
    # remove the unused kwargs
    missing_kwargs: set[str] = set()
    extra_kwargs: set[str] = set()
    for name, wa in init_attrs.items():
        src = wa.default_source
        # no default, required kwargs

        if src[0] == "required":
            assert (
                src[1] is None
            ), f"internal error: {self}.default_source ('required', {src[0]}) should be ('required', None)"
            if wa.init and name not in kwargs:
                missing_kwargs.add(name)
                continue
            else:
                value = kwargs.pop(name, Missing)
        # default with all the same instance
        elif src[0] == "default":
            value = kwargs.pop(name, src[1])
        # evaluate a factory function if there is not an argument
        elif src[0] == "default_factory":
            value = kwargs.pop(name, Missing)
            value = src[1]() if value is Missing else value
        # behind covering
        else:
            raise TypeError(f"internal error: unknown default_source kind {src[0]}")

        wa.init_attr(self, value)
    else:
        if len(missing_kwargs):
            raise TypeError(
                f"{self.__class__.__name__}(...) missing required kwarg(s) ({'=..., '.join(missing_kwargs)}=...)"
            )
        elif len(kwargs):
            raise TypeError(
                f"{self.__class__.__name__}(...) got unexpected kwarg(s) ({'=..., '.join(kwargs)}=...)"
            )

# ----------- init for WidgetAttrs class -----------
# NOTE: set the init for WidgetAttr since the type system cannot have one in the body
def _WidgetAttr__init__(
    self: WidgetAttr[_Attr],
    *,
    init: bool,
    build: bool = False,
    style: bool = False,
    default: _Attr | MissingType = Missing,
    default_factory: Callable[[], _Attr] | MissingType = Missing,
    kw_only: bool | MissingType = Missing,
) -> None:
    self.id = UID()
    self.build = build
    self.style = style
    # assing to this with None to reserve teh entries (b/c widgetattrs don't exits for themselves)
    self.private_name = None  # type: ignore[assignment]
    self.owning_cls = None  # type: ignore[assignment]
    self.name = None  # type: ignore[assignment]

    assert (init is True) or (
        init is False and kw_only is Missing
    ), f"can only use kw_only=... when init=True, found init={init} and kw_only={kw_only}"

    if init is False:
        assert (
            kw_only is Missing
        ), f"can only use kw_only=... when init=True, found init={init} and kw_only={kw_only}"
        self.kw_only = False
    else:
        self.kw_only = kw_only if kw_only is False else True

    self.init = init

    # parse the input

    if default is not Missing:
        assert default_factory is Missing, "cannot set both default and default_factory"
        self.default_source = ("default", default)
    elif default_factory is not Missing:
        self.default_source = ("default_factory", default_factory)
    else:
        self.default_source = ("required", None)


WidgetAttr.__init__ = _WidgetAttr__init__  # type: ignore[assignment]
