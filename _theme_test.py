try:
    from typing import (
        Type,
        ClassVar,
        TYPE_CHECKING,
        Iterable,
        Any,
        Optional,
        Union,
        Generic,
        TypeVar,
    )

    T = TypeVar("T")

    from enum import Enum, auto
except:
    TYPE_CHECKING = const(0)  # type:ignore
    auto = object  # type:ignore
    T = object  # type:ignore
    Generic = {object: object}  # type:ignore


class LabelSize:
    normal = auto()
    large = auto()


class LazyInheritedAttribute(Generic[T]):
    _climb_stack: list["Widget"] = []
    _climb_sentinel = object()

    def __init__(self, attrname: str, initial: T) -> None:
        # TODO: add doc string to decribe the funcitonality
        self._attrname = attrname
        self._priv_attrname = "_inherited_" + attrname + "_attr_"
        self._initial = initial

    def __repr__(self):
        return f"<InheritedAttribute: .{self._attrname}>"

    def __get__(self, owner: "Widget", ownertype: Type[object]) -> T:
        privname = self._priv_attrname

        # check that this attribute was initialized to the initial value in
        # the object's constructor, this is to enforce good behanvior
        assert hasattr(owner, privname), (
            f"`{owner}.{self._attrname}` attribute not initialized, "
            + f"inherited `{type(owner).__name__}.{self._attrname}` attributes must be "
            + f"initialized to the inital `{self._initial}` or some other value"
        )

        privattr = getattr(owner, privname)
        if privattr is not self._initial:  # normal get behavior
            return privattr
        else:  # get the inherited attribute

            self._climb_stack.append(owner)

            heirattr = getattr(owner._superior_, self._attrname, self._climb_sentinel)

            if heirattr is self._climb_sentinel:
                raise AttributeError(
                    f"unable to inherit .{self._attrname} attribute on {self._climb_stack[0]},"
                    + f"\nclimbed up {self._climb_stack}"
                )
            else:
                self._climb_stack.pop(-1)

            if heirattr is not self._initial:
                setattr(owner, privname, heirattr)
            return heirattr

    def __set__(self, owner, value) -> None:
        setattr(owner, self._priv_attrname, value)


if TYPE_CHECKING:
    InheritedAttribute = Union[
        None,
        T,
        LazyInheritedAttribute[Union[T, None]],
    ]
else:
    InheritedAttribute = {"Theme": object}


class StyledAttribute:
    def __init__(
        self,
        name: str,
        widtype: Type["Widget"],
        allowed: type | tuple[type, ...] = object,
    ) -> None:
        self._name = name
        self._widtype = widtype
        self._allowed = allowed

    def __get__(self, owner, ownertype=None):
        print(f"{owner}.__get__ '{self}' {ownertype}")

        if owner is None:
            return self

        name = self._name
        if name in owner._fixed_attrs_:
            value = owner._fixed_attrs_[name]
        else:
            value = owner._theme_[self._widtype][name]

        assert isinstance(value, self._allowed), (
            f"{owner}.{name} found object of {type(value)}, "
            + f"expected on of {self._allowed}"
        )
        return value

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:X {self._widtype.__name__}.{self._name}>"


# if not TYPE_CHECKING:
def themedwidget(widcls: "Type[Widget]") -> "Type[Widget]":

    for attr, allowed in widcls._fixed_style_attrs_.items():
        setattr(widcls, attr, StyledAttribute(attr, widcls, allowed))

    Theme._required_.add(widcls)

    # widcls._fixed_style_attrs_ = {
    #     attr: styledattr._allowed
    #     for attr in dir(widcls)
    #     if isinstance(styledattr := getattr(widcls, attr), StyledAttribute)
    # }

    return widcls


if TYPE_CHECKING:
    themedwidget = lambda cls: cls


class Widget:

    _superior_: Optional["Widget"]

    _theme_: ClassVar[InheritedAttribute["Theme"]] = LazyInheritedAttribute(
        "_theme_", None
    )

    _fixed_style_attrs_: ClassVar[dict[str, type | tuple[type, ...]]] = {
        "_margin_": int
    }

    def __init__(self, **styleattrs) -> None:

        # assert (  # that there are not extra keywords
        #     len(extras := set(styleattrs) - set(self._fixed_style_attrs_)) == 0
        # ), f"extra keyword argument{'s'*bool(len(extras) > 1)} {', '.join(name+'=' for name in extras)}"

        self._fixed_attrs_ = {
            name: styleattrs[name]
            for name in styleattrs
            if self._allows_fixed_style_attr_name(name)
        }

        self._superior_ = None
        self._theme_ = None
        super().__init__()

    def _allows_fixed_style_attr_name(self, name: str) -> bool:
        return isinstance(getattr(type(self), name, None), StyledAttribute)


class Theme:
    _required_: set[Type[Widget]] = {Widget}

    # defaults = {
    #     Widget: {"__margin__": 5},
    # }

    def __init__(self, styles: dict[Type[Widget], Any]) -> None:
        assert (
            len(missing := set(self._required_) - set(styles)) == 0
        ), f"missing styles for {missing}"
        assert (
            len(extras := set(styles) - set(self._required_)) == 0
        ), f"extras styles {extras}"


themedwidget(Widget)


@themedwidget
class Text(Widget):

    _fixed_style_attrs_ = {"fit": bool, "size": LabelSize}

    # _stateful_style_attrs = {"fill"}

    def __init__(self, text: str, **attrs) -> None:
        self._text = text
        super().__init__(**attrs)

    def __repr__(self) -> str:
        return f"<{type(self).__name__} {repr(self._text)}>"


@themedwidget
class Label(Text):
    _fixed_style_attrs_ = {"size": LabelSize}

    def __init__(self, text: str, **attrs) -> None:
        assert "\n" not in text
        super().__init__(text, **attrs)


class Date(Label):
    def __init__(self, src: str, **attrs) -> None:
        src.format(hour="17", min="01")
        self._src = src
        super().__init__(src, **attrs)


class Container(Widget):
    def __init__(self, *wids: Widget) -> None:
        super().__init__(_margin_=0)
        self._nested_ = wids
        for wid in wids:
            wid._superior_ = self


class Root(Container):

    _theme_ = Theme(
        {
            Widget: dict(_margin_=5),
            Text: dict(fit=True, size=LabelSize.normal),
            Label: dict(size=LabelSize.large),
        }
    )

    def __init__(self, wid: Widget) -> None:
        self._superior_ = None
        wid._superior_ = self
        self._nested_ = (wid,)


txt = Text("hello\nworld!")
lbl = Label("whitty title")
dt = Date("{hour}:{min}")

cntr = Container(txt, lbl, dt)
root = Root(cntr)
