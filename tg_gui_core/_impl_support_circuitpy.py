import sys
import builtins


def isoncircuitpython() -> bool:
    return True


from . import _circuitpy_compat_module

_circuitpy_compat_module.load_bypassed_modules()

from ._circuitpy_compat_module import enum_compat, GetItemBypass

# for mod in _circuitpy_compat_module.__bypassed_modules__:
#     sys.modules[mod] = _circuitpy_compat_module
_circuitpy_compat_module.load_bypassed_modules()


def warn(msg: str) -> None:
    print("WARNING: {msg}")


from ._circuitpy_compat_module import Generic as GenericABC  # type: ignore[attr-defined, misc]

MissingType = type("MissingType", (), {"__bool__": lambda self: False})
Missing = MissingType()
MissingType.__new__ = Missing  # type: ignore[assignment]


def generic_compat(cls: type):  # type: ignore[misc]
    cls.__generic_compat__ = True  # type: ignore[assignment]
    return GetItemBypass(cls.__name__, cls)


# --- isinstance and subclass helpers for _GenericBypass etc ---
class IsinstanceBase:
    pass
    # check_if_isinstance handled by isinstance_cp_compat


def isinstance_cp_compat(obj: object, classinfo: type | tuple[type, ...]) -> bool:
    classinfo = classinfo if _orig_isinstance(classinfo, tuple) else (classinfo,)
    # print("-----")

    # print("isinstance_cp_compat")
    # print(obj, classinfo)
    # print(tuple(hasattr(cls, "_inst_isinstance_check_") for cls in classinfo))
    # print(  # from tg_gui_core.shared import * ; isinstance(9, UID)
    #     tuple(
    #         (
    #             hasattr(cls, "_inst_isinstance_check_")
    #             and cls._inst_isinstance_check_(obj)  # type: ignore
    #         )
    #         for cls in classinfo
    #     )
    # )
    # print("-----")
    return any(
        _orig_isinstance(obj, cls)  # normal checking against a type
        if cls.__class__ is type
        else (
            hasattr(cls, "_inst_isinstance_check_")
            # and cls.__class__ is not type
            and cls._inst_isinstance_check_(obj)
        )
        for cls in classinfo
    )


def issubclass_cp_compat(cls, classinfo):
    classinfo = classinfo if _orig_isinstance(classinfo, tuple) else (classinfo,)
    # print(cls, classinfo)
    # print(tuple(_orig_issubclass(base, GetItemBypass) for base in classinfo))
    return any(
        _orig_issubclass(cls, base._value)
        if _orig_issubclass(base, GetItemBypass)
        else _orig_issubclass(cls, base)
        for base in classinfo
    )


_orig_isinstance = builtins.isinstance
_orig_issubclass = builtins.issubclass

builtins.isinstance = isinstance_cp_compat
builtins.issubclass = issubclass_cp_compat
