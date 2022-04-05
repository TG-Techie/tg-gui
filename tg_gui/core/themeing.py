from __future__ import annotations

from .implementation_support import isoncircuitpython
from ._shared import uid, UID
from .widget import Widget, InitAttr, _Missing


from typing import TYPE_CHECKING, TypeVar, Generic
from abc import ABC, abstractmethod

_T = TypeVar("_T")

# circular and annotation-only imports
if TYPE_CHECKING:
    from typing import Type, Any

    ThemeEntry = dict[InitAttr[_T], _T]
    ThemeDict = dict[Type[Widget], ThemeEntry]


def themedattr(*, default, repr=False, private_name=None, init=True):
    return ThemedAttr(default=default, repr=repr, private_name=private_name)


class Theme:

    if not __debug__:

        def __new__(cls, __entries: ThemeDict, _debug_name: str | None = None):
            return __entries

    def __init__(self, __entries: ThemeDict, _debug_name: str = "") -> None:
        self._id_ = uid()
        self._entries: ThemeDict = __entries
        if __debug__:
            self._debug_name: str = _debug_name

    def __getitem__(self, key: Type[Widget]) -> Any:
        return self._entries[key]

    def get(self, *args, **kwargs) -> Any:
        return self._entries.get(*args, **kwargs)

    if __debug__:

        def __set_name__(self, ownercls: type[Widget], name: str) -> None:
            self._debug_name = f"{ownercls.__module__}.{ownercls.__qualname__}.{name}"

        def __repr__(self) -> str:
            return f"<{type(self).__qualname__}: {self._id_} debug:{repr(self._debug_name or None)}>"

    else:

        def __repr__(self) -> str:
            return f"<{type(self).__qualname__}: {self._id_}>"


# circuitpython-compat(__class_getitem__) not supported
if not TYPE_CHECKING and isoncircuitpython():
    _InitAttr = InitAttr
    InitAttr = {_T: _InitAttr}


class ThemedAttr(InitAttr[_T]):

    _required_: bool = False
    _positional_: bool = False
    _build_: bool

    def __init__(
        self,
        *,
        default: _T,
        build: bool = False,
        repr: bool = False,
        private_name: str | None = None,
    ) -> None:
        self._build_ = build
        self._default: _T = default
        super().__init__(repr=repr, private_name=private_name)

    def get(self, owner: Widget) -> _T:
        attr = getattr(owner, self._private_name, _Missing)

        if attr is not _Missing:
            return attr

        # climb up the widger tree to find themes
        superior = owner._superior_
        while superior is not None:
            theme = superior._theme_
            if theme is None:
                continue
            for widcls in owner._iter_widgetcls_resolution():
                if theme.get(widcls, None) is not None:
                    attr = theme[widcls].get(self, _Missing)
                    if _Missing is not attr:
                        return attr
            else:
                superior = superior._superior_
        else:
            return self._default

    def _set_(self, owner: Widget, value: _T) -> None:
        setattr(owner, self._private_name, value)


# circuitpython-compat(__class_getitem__) finish
if not TYPE_CHECKING and isoncircuitpython():
    InitAttr = _InitAttr
    del _InitAttr
