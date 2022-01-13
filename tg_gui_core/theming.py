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

from ._shared import uid, UID, USE_TYPING, isoncircuitpython
from .base import Widget
from .stateful import State


from typing import TYPE_CHECKING, Generic, TypeVar

T = TypeVar("T")

if TYPE_CHECKING:
    from typing import *  # Protocol, ClassVar, Type, Any, TypeVar
    from .styled_widget import StyledWidget
    from .stateful import State

    _NotFound: object = type("NotFound", (), {})
    ()

    _StyleAttrSpec = dict[str, type | tuple[type, ...] | tuple[()]]

else:
    Protocol = {T: object}  # type: ignore
    _NotFound = object()


class ResolutionError(Exception):
    pass


if TYPE_CHECKING:
    themedwidget = lambda cls: cls


def themedwidget(cls: Type[StyledWidget]):
    build_attrs = None
    style_attrs = None

    for name in dir(cls):  # scan by name
        attr = getattr(cls, name)

        # skip not themed
        if name.startswith("_") or not isinstance(attr, ThemedAttribute):
            continue
        assert isinstance(attr, ThemedAttribute), f"found {attr}"

        # circuitpython does not have __set_name__, so add it
        if isoncircuitpython() and attr.name is None:
            attr.__set_name__(cls, name)

        # only add a new set of the attr names if there is a new build or style attr
        if attr.stylecls is cls:
            if attr.isbuildattr:
                if build_attrs is None:
                    build_attrs = set(cls._build_attrs_)
                build_attrs.add(attr.name)
            else:
                if style_attrs is None:
                    style_attrs = set(cls._style_attrs_)
                style_attrs.add(attr.name)
    else:
        # circuitpython does not support type.mro(), so we make an explicit list
        cls._stylecls_mro_ = (cls,) + cls._stylecls_mro_

        if build_attrs is not None:
            cls._build_attrs_ = frozenset(build_attrs)
        if style_attrs is not None:
            cls._style_attrs_ = frozenset(style_attrs)

        # register the class as required
        Theme._themed_widget_types_.add(cls)

    return cls


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

        while superior is not None and not superior._is_root_:
            superior = superior._superior_
            # move up the heirarchy if these is no theme entry
            if not hasattr(superior, "_theme_"):

                continue

            theme = superior._theme_
            if theme is None:
                continue

            for cls in widget._stylecls_mro_:
                # print((spec := theme.get(cls, False)), spec)
                if (spec := theme.get(cls, False)) and self in spec:
                    return spec[self]
            else:
                continue
        else:
            return self.default

        # raise ResolutionError(
        #     f"unable to resolve .{name} style attribute for {widget} (reached {superior})"
        # )

    def __repr__(self) -> str:

        if self.stylecls is None:
            f"<{type(self).__name__}: {self._id_} unlinked>"
        else:
            return f"<{type(self).__name__}: {self._id_} {self.stylecls.__name__}.{self.name}>"


if TYPE_CHECKING or USE_TYPING:

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
