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


from typing import TYPE_CHECKING, Generic, TypeVar

T = TypeVar("T")

if TYPE_CHECKING:
    from typing import *  # Protocol, ClassVar, Type, Any, TypeVar
    from .styled_widget import StyledWidget

    _NotFound: object = type("NotFound", (), {})
    ()

    _StyleAttrSpec = dict[str, type | tuple[type, ...] | tuple[()]]

else:
    Protocol = {T: object}  # type: ignore
    _NotFound = object()


class ResolutionError(Exception):
    pass


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
                    cls._build_attrs_ = build_attrs = set(cls._build_attrs_)
                build_attrs.add(attr.name)
            else:
                if style_attrs is None:
                    cls._style_attrs_ = style_attrs = set(cls._style_attrs_)
                style_attrs.add(attr.name)
    else:
        # circuitpython does not support type.mro(), so we make an explicit list
        cls._stylecls_mro_ = (cls,) + cls._stylecls_mro_

        # register the class as required
        Theme._required_.add(cls)

    return cls


class ThemedAttribute(Generic[T]):
    def __init__(
        self,
        # name: str,
        # stylecls: Type[StyledWidget],
        *,
        allowed: _StyleAttrSpec = (),
        isbuildattr: bool,
    ) -> None:
        self._id_ = uid()
        self.name: None | str = None
        self.stylecls: Type[StyledWidget] | None = None
        self.allowed = allowed
        self.isbuildattr = isbuildattr

    def __get__(self, owner: None | StyledWidget, ownertype: Type[StyledWidget]):
        if owner is None:
            return self  # circuitpython compat... also b/c what else would this do...?
        else:
            return self.get_themed_attr(owner)

    def __set__(self, owner: StyledWidget, value: Any) -> None:
        raise TypeError(
            f"{owner}.{self.name} is a themed attribute and cannot be set directly, wrap it in a State object"
        )

    def __set_name__(self, owner, name):
        self.name = name
        self.stylecls = owner

    def get_themed_attr(self, widget: StyledWidget) -> Any:
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

            for cls in widget._stylecls_mro_:
                # print((spec := theme.get(cls, False)), spec)
                if (spec := theme.get(cls, False)) and self in spec:
                    return spec[self]
            else:
                continue

        raise ResolutionError(
            f"unable to resolve .{name} style attribute for {widget} (reached {superior})"
        )

    def __repr__(self) -> str:

        if self.stylecls is None:
            f"<{type(self).__name__}: {self._id_} unlinked>"
        else:
            return f"<{type(self).__name__}: {self._id_} {self.stylecls.__name__}.{self.name}>"


if TYPE_CHECKING or USE_TYPING:

    class BuildAttribute(ThemedAttribute[T]):
        def __init__(self):
            super().__init__(isbuildattr=True)

    class StyledAttribute(ThemedAttribute[T]):
        def __init__(self):
            super().__init__(isbuildattr=False)

else:

    class _BuildAttribute(ThemedAttribute):
        def __init__(self):
            super().__init__(isbuildattr=True)

    class _StyledAttribute(ThemedAttribute):
        def __init__(self):
            super().__init__(isbuildattr=False)

    class _themed_attribute_sugar:
        def __init__(self, themecls: Type[ThemedAttribute]) -> None:
            self.themecls = themecls

        def __getitem__(self, allowed) -> Any:
            return self.themecls

    BuildAttribute = _themed_attribute_sugar(_BuildAttribute)
    StyledAttribute = _themed_attribute_sugar(_StyledAttribute)


class Theme(dict):
    _required_: ClassVar[set[Type[StyledWidget]]] = set()

    def __init__(self, specs, *, _debug_name_: str | None = None) -> None:
        self._id_ = uid()
        self.specs = specs
        self._debug_name_ = _debug_name_

    def __getitem__(self, key: StyledWidget) -> _VT:
        return self.specs[key]

    def get(self, *args):
        return self.specs.get(*args)

    def __repr__(self) -> str:
        dbg = f" {repr(self._debug_name_)}" if self._debug_name_ else ""
        return f"<{type(self).__name__}: {self._id_}{dbg}>"


class SubTheme(Theme):
    pass
