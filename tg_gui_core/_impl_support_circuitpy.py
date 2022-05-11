import sys
import builtins


def isoncircuitpython() -> bool:
    return True


from . import _circuitpy_compat_module

_circuitpy_compat_module.load_bypassed_modules()

from ._circuitpy_compat_module import enum_compat

for mod in _circuitpy_compat_module.__bypassed_modules__:
    sys.modules[mod] = _circuitpy_compat_module


def warn(msg: str) -> None:
    print("WARNING: {msg}")


from ._circuitpy_compat_module import Generic as GenericABC  # type: ignore[attr-defined, misc]

MissingType = type("MissingType", (), {"__bool__": lambda self: False})
Missing = MissingType()
MissingType.__new__ = Missing  # type: ignore[assignment]


def generic_compat(cls: type):  # type: ignore[misc]
    cls.__generirc_compat__ = True  # type: ignore[assignment]
    return _circuitpy_compat_module.GetItemBypass(cls.__name__, cls)


# --- isinstance and subclass helpers for _GenericBypass etc ---
class IsinstanceBase:
    pass
    # check_if_isinstance handled by isinstance_cp_compat


_orig_isinstance = builtins.isinstance
_orig_issubclass = builtins.issubclass


def isinstance_cp_compat(obj, classinfo: type | tuple[type, ...]) -> bool:
    classinfo = classinfo if _orig_isinstance(classinfo, tuple) else (classinfo,)
    return any(
        # from tg_gui_core.shared import * ; isinstance(9, UID)
        (
            hasattr(cls, "check_if_isinstance")
            and cls.check_if_isinstance(obj)  # type: ignore
        )
        or (_orig_isinstance(obj, cls))
        for cls in classinfo
    )


def issubclass_cp_compat(cls, classinfo):
    classinfo = classinfo if _orig_isinstance(classinfo, tuple) else (classinfo,)
    return any(
        _orig_issubclass(cls, base._value)
        if isinstance(base, _circuitpy_compat_module.GetItemBypass)
        else _orig_issubclass(cls, base)
        for base in classinfo
    )


builtins.isinstance = isinstance_cp_compat

builtins.issubclass = issubclass_cp_compat
