# The MIT License (MIT)
#
# Copyright (c) 2021 Jonah Yolles-Murphy (TG-Techie)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import annotations

from ._implementation_support import use_typing, isoncircuitpython
from .base import uid, UID, Widget
from .stateful import State


from typing import TYPE_CHECKING, Generic, TypeVar

T = TypeVar("T")

if TYPE_CHECKING:
    from typing import *  # Protocol, ClassVar, Type, Any, TypeVar
    from .styled_widget import StyledWidget
    from .stateful import State

    ThemeAttrsDict = Dict["ThemedAttribute", Any]
    ThemeCompatible = Union["Theme", dict[StyledWidget, ThemeAttrsDict]]


_NotFound = object()


class ResolutionError(Exception):
    pass


class ThemedAttribute(Generic[T]):
    isbuildattr: ClassVar[bool]

    if __debug__:

        def __new__(cls: Type[ThemedAttribute], *_, **__) -> ThemedAttribute:
            assert (
                cls is not ThemedAttribute
            ), f"{cls} is abstract, cannot make a instance of it. use BuildAttr or StyleAttr instead"
            return object.__new__(cls)

    def __init__(
        self,
        *,
        default: T,
    ) -> None:
        self._id_ = uid()

        self.name: None | str = None
        self.stylecls: Type[StyledWidget] | None = None

        self.default = default

    def __get__(self, owner: None | StyledWidget, ownertype: Type[StyledWidget]) -> T:
        if owner is None:
            # circuitpython compat... also b/c what else would this do...?
            return self  #
        else:
            return self.get_themed_attr(owner)

    def __set__(self, owner: StyledWidget, value: Any) -> None:
        raise TypeError(
            f"{owner}.{self.name} is a themed attribute and cannot be set directly, wrap it in a State object"
        )

    def __set_name__(self, owner: StyledWidget, name: str) -> None:
        assert (
            self.name is None and self.stylecls is None
        ), f"{self} alreay initialized (w/ __set_name__"
        self.name = name
        self.stylecls = owner

    def get_themed_attr(self, widget: StyledWidget) -> T:
        # check if it is passed directly
        name = self.name
        if name in widget._themed_attrs_:
            return widget._themed_attrs_[name]

        # climb up the widget heirarchy
        superior = widget

        while (
            superior is not None
            and hasattr(superior, "_is_root_")
            and not superior._is_root_
        ):
            superior = superior._superior_
            # move up the heirarchy if these is no theme entry
            if not hasattr(superior, "_theme_"):

                continue

            theme = superior._theme_
            if theme is None:
                continue

            # TODO: this may be needed for later `for cls in widget._stylecls_mro_`:
            curcls: Type[Widget] | Type[object] = type(widget)
            while curcls is not object:
                # print((spec := theme.get(cls, False)), spec)\
                spec = theme.get(curcls, None)
                if spec is not None and self in spec:
                    return spec[self]
                curcls = curcls.__bases__[0]
            else:
                continue
        else:
            return self.default

    def __repr__(self) -> str:

        if self.stylecls is None:
            f"<{type(self).__name__}: {self._id_} unlinked>"
        else:
            return f"<{type(self).__name__}: {self._id_} {self.stylecls.__name__}.{self.name}>"


if TYPE_CHECKING or use_typing():

    class BuildAttr(ThemedAttribute[T]):
        isbuildattr = True

    class StyledAttr(ThemedAttribute[T | State[T]]):
        isbuildattr = False

else:

    class BuildAttr(ThemedAttribute):
        isbuildattr = True

    class StyledAttr(ThemedAttribute):
        isbuildattr = False


class Theme(dict):
    _themed_widget_types_: ClassVar[set[Type[StyledWidget]]] = set()

    # optimization for memory usage
    if not __debug__:

        def __new__(self, specs, *, _debug_name_: str | None = None):
            return specs

    def __init__(self, specs, *, _debug_name_: str | None = None) -> None:
        self._id_ = uid()
        self.specs = specs
        self._debug_name_ = _debug_name_

        # TODO: add a check to make sure the input is valid.

    def __getitem__(self, key: StyledWidget) -> _VT:
        return self.specs[key]

    def get(self, *args):
        return self.specs.get(*args)

    def __repr__(self) -> str:
        dbg = f" {repr(self._debug_name_)}" if self._debug_name_ else ""
        return f"<{type(self).__name__}: {self._id_}{dbg}>"


# TODO: convert BuildAttr, StyledAttr into a WidgetAttr base and
# # move this bahavior into the Widget base class

# this could also open the door for attr = EviromentAttr(...) which
# would bind that attr to the same object in the enviroment (a but like themes...)


class ThemedWidget(Widget):
    _build_attrs_: ClassVar[set[str]] = frozenset()
    _style_attrs_: ClassVar[set[str]] = frozenset()

    _themed_attrs_: Dict[str, Any] = {}

    def __init__(
        self,
        # style=None,
        _margin_: int = None,
        **kwargs,
    ):

        super().__init__(_margin_=_margin_)

        # input validation
        if len(extra := set(kwargs) - (self._build_attrs_ | self._style_attrs_)):
            raise TypeError(
                f"{type(self).__name__}(...) got unexpected style attrs {extra}"
            )

        self._themed_attrs_ = kwargs

    @classmethod
    def _subclass_format_(cls: Type[ThemedWidget], subcls: Type[ThemedWidget]):
        build_attrs = set()
        style_attrs = set()

        # print(f"{cls}._subclass_format_({subcls})")

        for name, attr in subcls.__dict__.items():
            if isinstance(attr, BuildAttr):
                assert (
                    attr.name is not None
                ), f"{attr} has no name (__set_name__ not called?)"
                build_attrs.add(name)
            elif isinstance(attr, StyledAttr):
                assert (
                    attr.name is not None
                ), f"{attr} has no name (__set_name__ not called?)"
                style_attrs.add(name)
            else:
                pass
        else:
            if len(build_attrs):
                subcls._build_attrs_ = frozenset(build_attrs | subcls._build_attrs_)
            if len(style_attrs):
                subcls._style_attrs_ = frozenset(style_attrs | subcls._style_attrs_)
        return subcls
