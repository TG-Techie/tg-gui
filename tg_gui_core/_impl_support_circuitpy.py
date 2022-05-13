import sys
import builtins


def isoncircuitpython() -> bool:
    return True


def warn(msg: str) -> None:
    print("WARNING: {msg}")


from . import _circuitpy_compat_module

_circuitpy_compat_module.load_bypassed_modules()

MissingType = type("MissingType", (), {"__bool__": lambda self: False})
Missing = MissingType()
MissingType.__new__ = Missing  # type: ignore[assignment]

# --- isinstance and subclass helpers for _GenericBypass etc ---
class IsinstanceBase:
    pass
    # check_if_isinstance handled by isinstance_cp_compat


def isinstance_cp_compat(obj: object, classinfo: type | tuple[type, ...]) -> bool:
    classinfo = classinfo if _orig_isinstance(classinfo, tuple) else (classinfo,)
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


_orig_isinstance = builtins.isinstance

builtins.isinstance = isinstance_cp_compat
