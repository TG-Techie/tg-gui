from __future__ import annotations

from typing import TYPE_CHECKING, TypeVar, Generic

_T = TypeVar("_T")


class State(Generic[_T]):
    def __init__(self) -> None:
        raise NotImplementedError
