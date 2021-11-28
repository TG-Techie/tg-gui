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

from .. import uid
from ..base import Widget
from .style import Style, _errfmt
from .styled_widget import StyledWidget

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import *

    Styling = Union[Style, Mapping[str, Any]]
    StylingMapping = Mapping[Type[StyledWidget], Styling]


def themedwidget(cls):
    """
    @decorator
    registers as requiring a style entry in Themes
    # TODO: consider if this should be a classmethod on theme subclasses
    """
    assert issubclass(cls, StyledWidget)
    assert isinstance(cls._stateful_style_attrs_, (set, dict))
    assert isinstance(cls._stateful_style_attrs_, (set, dict))

    assert cls._offer_priority_ is not None, f"{cls}._offer_priority_ not specified"
    assert cls._reserve_space_ is not None, f"{cls}._reserve_space_ not specified"
    assert cls._self_sizing_ is not None, f"{cls}._self_sizing_ not specified"

    Theme._required_styles_ |= {cls}  # add this to Theme's required styles

    if hasattr(cls, "_default_styling_"):
        assert cls not in Theme._decld_default_styling_dict, cls
        Theme._decld_default_styling_dict[cls] = cls._default_styling_

    return cls


class Theme:
    _required_styles_: set[str] = set()
    _decld_default_styling_dict: dict[Type[Widget], dict[str, Any]] = {}

    def get_styling_for(self, cls: Type[StyledWidget]):
        return self._stylings[cls]

    # fn name remapping
    __call__ = get_styling_for
    _get_base_styling_for_ = get_styling_for

    def __get__(self, owner, ownertype):
        return self

    def __set__(self, owner, value):
        assert value is None or value is self, (
            "themes cannot be overwritten once assinged, "
            + f"only assign them to themselves or None (has no effect). "
            + f"tried: `{owner._theme_} = {value}`"
        )

    def __init__(self, stylings: StylingMapping):
        self._id_ = uid()

        self._verify_complies(stylings)
        self._stylings = stylings
        # TODO: add margin argument
        # self._margin = margin

    def __repr__(self):
        return f"<{type(self).__name__}:{self._id_}>"

    def _verify_complies(self, styles):

        req_styles = self._required_styles_
        # check they keys match
        assert len(req_styles) == len(styles), (
            f"incorrect number of style defaults given,\n"
            + f"found {_errfmt(cls.__qualname__ for cls in styles)},\n"
            + f"expected {_errfmt(cls.__qualname__ for cls in req_styles)}\n"
        )

        assert all(style_type in styles for style_type in req_styles), (
            "invalid entry passsed to theme on init "
            + f"{_errfmt(set(styles) - req_styles)})"
        )
        # check that each styles entry compiles with Tuple[Dict[], Dict[]]
        for style_type, entry in styles.items():
            assert isinstance(entry, dict)
            stateful, fixed = (
                style_type._stateful_style_attrs_,
                style_type._fixed_style_attrs_,
            )

            assert len(entry) == (len(fixed) + 1), (
                f"incorrect number of style attributes given for {style_type},\n"
                + f"should be {_errfmt(set(['style']) | set(fixed))},\n"
                + f"found {_errfmt(set(entry))}"
            )

            assert ("style" in entry) and all(
                (attrname in entry) for attrname in fixed
            ), (
                f"unexpected style attrivute in foudn for {style_type},\n"
                + f"should only  be {_errfmt(stateful | fixed)},\n"
                + f"found {_errfmt(set(entry))}"
            )


class SubTheme(Theme):
    def __get__(self, owner, ownertype=None):
        """
        This is a mechanism to automatically bind
        """

        if not self._isconfigured():
            # print("__get__", owner, owner._superior_, owner._superior_._theme_)
            self._configure_base_theme_(owner._superior_._theme_)
        return self

    def __init__(self, *args):
        self._id_ = uid()

        theme: None | Theme
        overrides: StylingMapping

        if len(args) == 2:
            theme, overrides = args
        elif len(args) == 1:
            (overrides,) = args
            theme = None
        else:
            raise ValueError(
                f"too many or too few arguments provided. expected 1 or 2, found {len(args)}"
            )

        assert isinstance(overrides, dict)
        assert theme is None or isinstance(theme, Theme)

        self._theme = theme
        self._overrides = overrides

        if theme is not None:
            self._configure_for(theme)

    def _configure_base_theme_(self, theme: Theme):
        # assert theme is not self
        if theme is self:
            return
        assert isinstance(theme, Theme)

        if self._isconfigured():
            assert self._theme._id_ is theme._id_, f"misconfiged theme for style fetch"
        else:
            self._configure_for(theme)

        return self

    def get_styling_for(self, cls):
        assert self._isconfigured()
        if cls in self._overrides:
            return self._overrides[cls]
        else:
            return self._theme.get_styling_for(cls)

    def _get_base_styling_for_(self, cls):
        return self._theme._get_base_styling_for_(cls)

    def _isconfigured(self):
        return self._theme is not None

    def _configure_for(self, theme: Theme):
        assert isinstance(
            theme, Theme
        ), f"expected an object of type Theme, found {type(theme).__name__}"

        self._theme = theme

        self._overrides = {
            cls: {
                attrname: ovrds.get(attrname, theme_entry)
                for attrname, theme_entry in theme.get_styling_for(cls).items()
            }
            for cls, ovrds in self._overrides.items()
        }

        for cls, ovrds in self._overrides.items():
            style = ovrds.get("style", None)
            if style is not None and isinstance(style, Style):
                style._configure_(cls, self)
