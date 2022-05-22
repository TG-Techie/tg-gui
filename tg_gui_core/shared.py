from __future__ import annotations

from typing import Protocol
from .implementation_support import annotation_only


if annotation_only():
    from typing import TypeGuard, Any

    class Identifiable(Protocol):
        @property
        def id(self) -> UID:
            ...

else:
    Identifiable = object

from .implementation_support import (
    Missing,
    MissingType,
    IsinstanceBase,
)


Pixels = int


def add_pixel_pair(
    __a: tuple[Pixels, Pixels], __b: tuple[Pixels, Pixels]
) -> tuple[Pixels, Pixels]:
    return (__a[0] + __b[0], __a[1] + __b[1])


def id_attr_as_int(obj: Identifiable) -> int:
    return int(obj.id)  # type: ignore


class UID(IsinstanceBase):

    __next_int: int = 0

    def __new__(cls) -> "UID":
        new_uid = cls.__next_int
        cls.__next_int += 1
        return new_uid  # type: ignore

    def __init__(self, *_, **__) -> None:  # pyright: reportMissingSuperCall=false
        raise RuntimeError(
            "UID.__init__ called. "
            "UID() should return an int (shhhh) and never be given an argument, "
            "thus __init__ should not be called",
        )

    @classmethod
    def check_if_isinstance(cls, __instance) -> bool:
        return isinstance(__instance, int) and __instance >= 0
