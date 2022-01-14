import sys

TYPE_CHECKING = False

try:
    from typing import *

    raise RuntimeError
except ImportError:
    pass
except RuntimeError:
    raise ImportError(
        "tried importing cpython_bypass when the typing module, types module, or enum module is avaible "
        + "(You should not need to use tg_gui_core.typing_bypass in "
        + "a context where the typing module can be imported)"
    )

# --- typing bypass ---
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
builtins.Union = Union = Bypass("Union", type)  # type: ignore
builtins.TypeVar = TypeVar = lambda *_, **__: object  # type: ignore


# --- types bypass ---
FunctionType = type(lambda: None)
BuiltinFunctionType = type(print)
assert FunctionType is not BuiltinFunctionType

MethodType = type(Generic.__getitem__)
BuiltinMethodType = type({}.update)
# no assert as this the same

# --- enum bypass ---


class Enum:
    if __debug__:
        _compat_wrapped_ = False

    def __new__(cls, *_, **__):
        raise TypeError(
            f"Cannot make Enum '{cls.__name__}' instances on circuitpython, "
            + "decorate the class with @enum_compat"
        )

    def __init__(self, name: str, autoid: int):
        if __debug__:
            assert (
                self._compat_wrapped_
            ), f"{self.__class__.__name__} is not wrapped with @enum_compat"

        self._name: str = name
        # self._outer: type = outer
        self._vrnt_id = autoid

    def __eq__(self, other):
        return (
            self._vrnt_id == other._vrnt_id if isinstance(other, type(self)) else False
        )

    def __hash__(self):
        return hash(repr(self)) ^ hash(self._vrnt_id)

    def __repr__(self):
        return f"<{type(self).__name__}.{self._name}: {self._vrnt_id}>"


auto = lambda: None


def enum_compat(cls: type):

    assert issubclass(cls, Enum)

    if __debug__:
        cls._compat_wrapped_ = True

    cls.__new__ = lambda cls, *_: object.__new__(cls)  # type: ignore

    autoid = 0
    for name in dir(cls):
        attr = getattr(cls, name)

        if name.startswith("__") or callable(attr):
            continue

        if isinstance(attr, int):
            autoid = attr
        else:
            autoid += 1
        setattr(cls, name, cls(name, autoid))

    cls.__new__ = Enum.__new__  # type: ignore
    cls.__init__ = None  # type: ignore

    return cls
