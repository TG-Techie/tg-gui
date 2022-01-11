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

from ._shared import uid, UID, USE_TYPING
from .base import Widget


from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import *  # Protocol, ClassVar, Type, Any, TypeVar
    from .styled_widget import StyledWidget

    T = TypeVar("T")
    _NotFound: object = type(
        "NotFound",
        (),
        dict(__repr__=lambda _: "<NotFound (tg-gui internal object)>"),
    )()

    _StyleAttrSpec = dict[str, type | tuple[type, ...] | tuple[()]]

else:
    T = None  # type: ignore
    Protocol = {T: object}  # type: ignore
    _NotFound = object()


class ResolutionError(Exception):
    pass


def themedwidget(
    *,
    buildattrs: _StyleAttrSpec | None = None,
    statefulattrs: _StyleAttrSpec | None = None,
) -> Type[StyledWidget]:
    """
    A decorator that injects the themed attributes in format the subclasses for styled widgets
    """
    buildattrs = {} if buildattrs is None else buildattrs
    statefulattrs = {} if statefulattrs is None else statefulattrs

    return lambda cls: _themedwidget(cls, Theme, buildattrs, statefulattrs)


def _themedwidget(
    cls: Type[StyledWidget],
    register_to: Type[Theme],
    buildattrs: _StyleAttrSpec,
    statefulattrs: _StyleAttrSpec,
) -> Type[StyledWidget]:
    """
    the actual formatter and themeifier so to speak
    """

    buildattr_names = set(buildattrs)
    statefulattr_names = set(statefulattrs)

    # validate the build and stateful attrs
    assert len(overlapping := buildattr_names & statefulattr_names) == 0, (
        f"conflicting build and style attributes for "
        + f"@themedwidget(...)(class {cls.__name__}) , found {overlapping} in both"
    )

    # link the this class into the resolution order
    cls._stylecls_mro_ = (cls,) + cls._stylecls_mro_

    # --- inject sets of attrs ---
    # spr_buildattrs , spr_statefulattrs= cls._build_style_attrs_,cls._stateful_style_attrs_
    if len(buildattr_names):
        cls._build_style_attrs_ = cls._build_style_attrs_ | buildattr_names
    else:
        cls._build_style_attrs_ = cls._build_style_attrs_

    if len(statefulattr_names):
        cls._stateful_style_attrs_ = cls._stateful_style_attrs_ | statefulattr_names
    else:
        cls._stateful_style_attrs_ = cls._stateful_style_attrs_

    # --- inject the themed attribute descriptors ---
    for name, allowed in buildattrs.items():
        setattr(cls, name, ThemedAttribute(name, cls, allowed, isbuildattr=True))

    for name, allowed in statefulattrs.items():
        print(
            cls,
            name,
        )
        setattr(cls, name, ThemedAttribute(name, cls, allowed, isbuildattr=False))

    return cls


class ThemedAttribute:
    def __init__(
        self,
        name: str,
        stylecls: Type[StyledWidget],
        allowed: _StyleAttrSpec,
        isbuildattr: bool,
    ) -> None:
        self.name = name
        self.stylecls = stylecls
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

    def get_themed_attr(self, widget: StyledWidget) -> Any:
        # check if it is passed directly
        name = self.name
        if name in widget._style_attrs_:
            return widget._style_attrs_[name]

        # climb up the widget heirarchy
        superior = widget

        while superior is not None and not superior._is_root_:
            superior = superior._superior_
            # move up the heirarchy if these is no theme entry
            if not hasattr(superior, "_theme_"):

                continue

            theme = superior._theme_

            for cls in widget._stylecls_mro_:
                if (spec := theme.get(cls, False)) and self in spec:
                    return spec[self]
            else:
                continue

        raise ResolutionError(
            f"unable to resolve .{name} style attribute for {widget} (reached {superior})"
        )


class Theme(dict):
    pass


class SubTheme(Theme):
    pass


if TYPE_CHECKING:
    themedwidget = lambda cls: cls
