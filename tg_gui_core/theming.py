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

from ._shared import uid, UID, enum_compat, USE_TYPING
from .base import Widget
from .style import Style, _errfmt
from .root_widget import Root

from enum import Enum, auto

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import *  # Protocol, ClassVar, Type, Any, TypeVar
    from .styled_widget import StyledWidget

    _NotFound: object = type("NotFound", (), {})()
    T = TypeVar("T")


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
        stateful: bool,
        widtype: Type["StyledWidget"],
        allowed: type | tuple[type, ...] = object,
    ) -> None:

        self.name = name
        self.widtype = widtype

        if USE_TYPING:
            from .styled_widget import StyledWidget

            assert issubclass(widtype, StyledWidget)

        self.allowed = allowed
        self._stateful = stateful

    def __get__(self, owner: None | "StyledWidget", ownertype: Type["StyledWidget"]):
        if owner is None:
            return self

        assert owner is not None

        name = self.name
        stateful = self._stateful

        inst_attr_dict = owner._stateful_attrs_ if stateful else owner._build_attrs_
        attr = inst_attr_dict.get(name, _NotFound)

        if attr is _NotFound:
            theme = owner._superior_._theme_
            assert theme is not None
            attr = theme.getattr(
                self.widtype,  # type(owner),
                name,
                _debug_widget=owner,
            )

        assert isinstance(attr, self.allowed), (
            f"{owner}.{name} found object of {type(attr)}, "
            + f"expected one of {self.allowed}"
        )

        return attr

    def __repr__(self) -> str:
        return f"<{type(self).__name__}:X {self.widtype.__name__}.{self.name}>"


class Theme:
    _required_: set[Type["StyledWidget"]] = set()

    _check_for_missing: ClassVar[bool] = True

    def __init__(
        self,
        *,
        margin: int | None,
        styling: dict[Type["StyledWidget"], dict[str, Any]],
    ) -> None:

        self._check_styling_against_spec(styling)

        self._id_ = uid()
        self._margin = margin
        self._source = styling

        self._is_linked = False
        self._superior_theme_: None | Theme = None
        self._linked_widget_id_: None | UID = None

    def __get__(self, owner, ownertype):
        return self

    def __set__(self, owner, value):
        assert value is None

    def _is_linked_(self) -> bool:
        return self._is_linked

    def _link_on_nest_(self, widget: StyledWidget) -> None:
        assert self._is_linked is False, f"{self} is already linked"

        # climb the widget tree to find the nearest theme above this one
        superior_widget = widget
        superior_theme = widget._theme_
        while superior_theme is self:
            superior_widget = superior_widget._superior_
            superior_theme = superior_widget._theme_
        else:
            self._superior_theme_ = superior_theme

        self._is_linked = True
        self._linked_widget_id_ = widget._id_

    def _unlink_on_unnest_(self, widget: StyledWidget) -> None:
        self._required_.remove(widget)

        if widget._id_ is self._linked_widget_id_:
            self._superior_theme_ = None
            self._is_linked = False

    def getmargin(self, widget: StyledWidget) -> int:
        return self._margin

    def getattr(
        self,
        widgetcls: Type[StyledWidget],
        name: str,
        *,
        _debug_widget: None | Widget = None,
        _return_guard: bool = False,
    ) -> Any:
        assert isinstance(widgetcls, type)

        attrs = self._source.get(widgetcls, _NotFound)

        # error if it is not found
        if attrs is _NotFound:
            if _return_guard:
                return _NotFound
            else:
                raise ResolutionError(
                    f"{self} has no entry for {widgetcls} at "
                    + ("unknown" if _debug_widget is None else str(_debug_widget))
                    + f" for the .{name} attribute, is it themed?"
                )

        # otherwise, get the attribute internally (w/ return guard)
        attr = attrs.get(name, _NotFound)
        if attr is not _NotFound:
            return attr
        elif _return_guard:
            return _NotFound
        else:
            # raise an error
            wid_dbg_str = (
                f"on widget of type {widgetcls}"
                if _debug_widget is None
                else f" on {_debug_widget}"
            )
            raise ResolutionError(
                f"cannot resolve themed attribute `.{name}` {wid_dbg_str}"
            )

    def __repr__(self) -> str:
        return f"<{type(self).__name__}: {self._id_}>"

    @classmethod
    def _check_styling_against_spec(
        cls, styling: dict[Type["StyledWidget"], dict[str, Any]]
    ) -> None:
        assert (
            len(extra := set(styling) - set(cls._required_)) == 0
        ), f"extra style_attrs {extra}"

        if cls._check_for_missing:

            assert (
                len(missing := set(cls._required_) - set(styling)) == 0
            ), f"missing style_attrs for {missing}"

        for widcls, attrs in styling.items():

            assert (
                len(extra := set(attrs) - widcls._all_style_attr_names_) == 0
            ), f"extra style attrs {extra} for {widcls} entry in {cls}"

            if cls._check_for_missing:
                assert (
                    len(missing := widcls._all_style_attr_names_ - set(attrs)) == 0
                ), f"missing style attrs {missing} for {widcls} entry in {cls}"


class SubTheme(Theme):

    _check_for_missing: ClassVar[bool] = False

    def __init__(
        self,
        styling: dict[Type["StyledWidget"], dict[str, any]],
    ) -> None:

        super().__init__(margin=None, styling=styling)

    def _find_superior(self, widget: StyledWidget) -> None | tuple[Widget, Theme]:

        super_widget = widget
        super_theme = widget._theme_
        while super_theme is self:
            super_widget = super_widget._superior_
            super_theme = super_widget._theme_
        else:
            assert super_theme is not self
            return super_widget, super_theme

    def getmargin(self, widget: Widget) -> int:
        return self._find_super_theme().getmargin(widget)
        # return widget._superior_._theme_.getmargin(widget)

    def getattr(
        self,
        widgetcls: Type[StyledWidget],
        name: str,
        *,
        _debug_widget: None | Widget = None,
        _return_guard: bool = False,
    ) -> Any:
        attr = super().getattr(
            widgetcls, name, _debug_widget=_debug_widget, _return_guard=True
        )

        if attr is _NotFound:
            attr = self._superior_theme_.getattr(
                widgetcls, name, _debug_widget=_debug_widget
            )

        if attr is not _NotFound:
            return attr
        elif _return_guard:
            return _NotFound
        else:
            raise ResolutionError(
                f"{self} has no entry for {widgetcls} at "
                + +("unknown" if _debug_widget is None else _debug_widget)
                + ", is it themed?"
            )


# shared objects required for styling


@enum_compat
class align(Enum):
    leading = auto()
    center = auto()
    trailing = auto()
