from __future__ import annotations

from ._implementation_support_ import isoncircuitpython
from ._shared_ import uid, UID
from .widget import Widget, InitAttr


from typing import TYPE_CHECKING, TypeVar, Generic
from abc import ABC, abstractmethod

_T = TypeVar("_T")

# circular and annotation-only imports
if TYPE_CHECKING:
    from typing import Type, Any, overload, Literal


class Theme:

    if not __debug__:

        def __new__(self, __entries: dict, _debug: str | None = None):
            return __entries

    def __init__(self, __entries, _debug: str | None = None) -> None:
        self._entries = __entries
        self._debug = _debug

    def __getitem__(self, key: str) -> Any:
        return self._entries[key]

    def get(self, *args, **kwargs) -> Any:
        return self._entries.get(*args, **kwargs)

    def __repr__(self) -> str:
        raise NotImplementedError(super().__repr__())


# circuitpython compat or generic InitAttribute
if not TYPE_CHECKING and isoncircuitpython():
    _InitAttribute = InitAttribute
    InitAttribute = {_T: _InitAttribute}


class ThemedAttribute(InitAttr[_T]):

    _stateful = False

    def __init__(self, *, default: _T, private_name: str | None = None) -> None:
        self._default = default
        super().__init__(private_name=private_name)

    def get(self, *_, **__):
        raise NotImplementedError


# circuitpython compat or generic ThemedAttribute
if not TYPE_CHECKING and isoncircuitpython():
    _ThemedAttribute = ThemedAttribute
    ThemedAttribute = {_T: _ThemedAttribute}


class BuildAttribute(ThemedAttribute[_T]):
    pass


class StyleAttribute(ThemedAttribute[_T]):
    def __init__(self, *, default: _T, stateful: bool = True) -> None:
        self._stateful = stateful
        super().__init__(default=default)


if not TYPE_CHECKING and isoncircuitpython():
    InitAttribute = _InitAttribute
    del _InitAttribute
