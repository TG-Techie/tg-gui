from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeGuard, Any


from .implementation_support import Missing, MissingType, IsinstanceBase


Pixels = int


class UID(IsinstanceBase):

    __next_int: int = 0

    def __new__(cls) -> "UID":
        new_uid = cls.__next_int
        cls.__next_int += 1
        return new_uid  # type: ignore

    @classmethod
    def __isinstance_hook__(cls, __instance) -> bool:
        return isinstance(__instance, int) and __instance >= 0


class Identifiable:
    id: UID
