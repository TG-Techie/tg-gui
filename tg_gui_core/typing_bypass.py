import sys

TYPE_CHECKING = False

try:
    from typing import *

    raise RuntimeError
except ImportError:
    pass
except RuntimeError:
    raise ImportError(
        "tried importing typing _bypass when the typing module is avaible "
        + "(You should not need to use tg_gui_core.typing_bypass in "
        + "a context where the typing module can be imported)"
    )


class Bypass:

    _getitem_return_value___: object

    def __init__(
        self,
        __name: str,
        ___getitem: list[object] | Type[type] = [],
        **attrs: object,
    ) -> None:
        self.__name = __name

        assert (
            ___getitem is type
            or isinstance(___getitem, list)
            and (len(___getitem) in {0, 1})
        ), f"expected the `type` object, an empty list, a list containing one item, got {___getitem}"

        if ___getitem is type:
            self._getitem_return_value___ = type(__name + "Bypass", (), {})
        elif isinstance(___getitem, list) and len(___getitem) == 1:
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

builtins.Generic = Generic = Bypass("Generic", type)  # type: ignore
builtins.TypeVar = TypeVar = lambda *_, **__: object  # type: ignore
