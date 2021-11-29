import sys

TYPE_CHECKING = False


class Bypass:
    def __init__(self, __name: str, ___getitem=[], **attrs: object) -> None:
        self.__name = __name

        assert isinstance(___getitem, list) and (
            len(___getitem) in {0, 1}
        ), f"expected an empty list or list containing one item, got {___getitem}"

        if len(___getitem) == 0:
            pass
        elif len(___getitem) == 1:
            self._getitem_return_value___ = ___getitem[0]

        for attr, obj in attrs.items():
            setattr(self, attr, obj)

    def __getitem__(self, *args):
        if not hasattr(self, "_getitem_return_value___"):
            raise TypeError(
                f"{repr(self)} does not support `{self.__name}[{','.join(repr(arg) for arg in args)}]`"
            )
        return self._getitem_return_value___

    def __repr__(self) -> str:
        return f"<{type(self).__name__} '{self.__name}'>"


# patch in __future__ bypass
sys.modules["__future__"] = Bypass("__future__", [], annotations=None)  # type: ignore

# patch in things the gramar cannot get rid of
import builtins

builtins.Generic = Generic = Bypass("Generic", [object])  # type: ignore
builtins.TypeVar = TypeVar = lambda *_, **__: object  # type: ignore
