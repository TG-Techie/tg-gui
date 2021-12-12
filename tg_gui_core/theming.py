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

from ._shared import uid, enum_compat, USE_TYPING
from .base import Widget
from .style import Style, _errfmt

from enum import Enum, auto

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import *  # Protocol, ClassVar, Type, Any, TypeVar
    from .styled_widget import StyledWidget

    _NotFound: object = type("NotFound", (), {})()
    T = TypeVar("T")

    class ThemeDictItem(TypedDict):
        fixed: dict[str, Any]
        stateful: dict[str, Any]

else:
    T = None  # type: ignore
    Protocol = {T: object}  # type: ignore
    _NotFound = object()


class ResolutionError(AttributeError):
    pass


class ThemedAttribute:

    _attr_may_be_stateful: ClassVar[bool]

    name: str
    widtype: Type["StyledWidget"]
    allowed: type | tuple[type, ...] = object

    def __init__(
        self,
        name: str,
        widtype: Type["StyledWidget"],
        allowed: type | tuple[type, ...] = object,
    ) -> None:
        assert (
            type(self) is not ThemedAttribute
        ), f"cannot init a non-subclasses ThemedAttribute"
        self.name = name
        self.widtype = widtype

        if USE_TYPING:
            from .styled_widget import StyledWidget

            assert issubclass(widtype, StyledWidget)

        self.allowed = allowed

    def __get__(self, owner: None | "StyledWidget", ownertype: Type["StyledWidget"]):
        if owner is None:
            return self
        assert owner is not None

        name = self.name
        maybe_stateful = self._attr_may_be_stateful

        inst_attr_dict = (
            owner._stateful_attrs_ if maybe_stateful else owner._build_attrs_
        )
        attr = inst_attr_dict.get(name, _NotFound)

        if attr is _NotFound:
            theme = owner._theme_
            assert theme is not None

            if maybe_stateful:
                attr = theme.getstatefulattr(self.widtype, name, owner)
            else:
                attr = theme.getbuildattr(self.widtype, name, owner)

        assert isinstance(attr, self.allowed), (
            f"{owner}.{name} found object of {type(attr)}, "
            + f"expected on of {self.allowed}"
        )

        return attr

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:X {self.widtype.__name__}.{self.name}>"


class ThemedBuildAttribute(ThemedAttribute):
    _attr_may_be_stateful = False


class ThemedStatefulAttribute(ThemedBuildAttribute):
    _attr_may_be_stateful = True


class Theme:
    _required_: set[Type["StyledWidget"]] = set()

    _check_completeness: ClassVar[bool] = True

    def __init__(
        self,
        *,
        margin: int,
        styling: dict[Type["StyledWidget"], ThemeDictItem],
    ) -> None:

        if self._check_completeness:
            assert (
                len(extra := set(styling) - set(self._required_)) == 0
            ), f"extra style_attrs {extra}"

            assert (
                len(missing := set(self._required_) - set(styling)) == 0
            ), f"missing style_attrs for {missing}"

        self._margin = margin
        self._source = styling

        # TODO: assert self._check_styles()

    def __get__(self, owner, ownertype):

        return self

    def __set__(self, owner, value):
        assert value is None

    def getmargin(self, widget: StyledWidget) -> int:
        return self._margin

    def getbuildattr(
        self, widcls: Type[StyledWidget], name: str, debug_widget: None | Widget = None
    ):
        return self._get_attr(widcls, name, False, debug_widget=debug_widget)

    def getstatefulattr(
        self, widcls: Type[StyledWidget], name: str, debug_widget: None | Widget = None
    ):
        return self._get_attr(widcls, name, True, debug_widget=debug_widget)

    def _get_attr(
        self,
        widget: StyledWidget,
        name: str,
        is_stateful: bool,
        debug_widget: None | Widget,
        _return_guard: bool = False,
    ) -> Any:

        widcls = type(widget)
        print(self._source)
        pack = self._source.get(widcls, _NotFound)

        if pack is _NotFound:
            wid_dbg_str = "" if debug_widget is None else f"(from {debug_widget})"
            raise ResolutionError(
                f"{self} has not themse entries for {widcls} at all {wid_dbg_str}, is it themed?"
            )

        print(pack)
        attrs = pack["stateful"] if is_stateful else pack["build"]

        value = attrs.get(name, _NotFound)
        if value is not _NotFound:
            return value
        elif _return_guard:
            return _NotFound
        else:
            kind = "stateful" if is_stateful else "build"
            wid_dbg_str = (
                f"on widget of type {widcls}"
                if debug_widget is None
                else f" on {debug_widget}"
            )
            raise ResolutionError(
                f"cannot resolve themed {kind} attribute .{name} {wid_dbg_str}"
            )


class SubTheme(Theme):
    _check_completeness: ClassVar[bool] = False

    def __init__(
        self,
        styling: dict[
            Type["StyledWidget"],
            dict[str, any],
        ],
    ) -> None:

        self._styling = styling

    def getmargin(self, widget: Widget) -> int:
        return widget._superior_._theme_.getmargin(widget)

    def _get_attr(
        self,
        widget: StyledWidget,
        name: str,
        is_stateful: bool,
        debug_widget: None | Widget,
    ) -> Any:

        print(self, self._styling[type(widget)])

        maybe_attr: Any = self._styling[type(widget)].get(name, _NotFound)

        if maybe_attr is not _NotFound:
            return maybe_attr
        else:
            return widget._superior_._theme_._get_attr(
                widget,
                name,
                is_stateful,
                debug_widget,
            )


# shared objects required for styling


@enum_compat
class align(Enum):
    leading = auto()
    center = auto()
    trailing = auto()
