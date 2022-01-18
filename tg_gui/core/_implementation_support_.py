import sys


# TODO: maybe pre-process `sys.implementation.name` here?
if sys.implementation.name == "cpython":
    from typing import TypeVar, Generic, Callable
    from abc import ABCMeta

    def isoncircuitpython() -> bool:
        return False

    class_id = id
    enum_compat = lambda cls: cls

    def warn(msg: str) -> None:
        raise Warning(msg)

    _T = TypeVar("_T")

    class GenericABC(Generic[_T], metaclass=ABCMeta):
        pass

    from functools import wraps as _wraps


elif sys.implementation.name == "circuitpython":

    def isoncircuitpython() -> bool:
        return True

    class_id = lambda cls: hash(f"(:{cls.__module__}.{cls.__qualname__})")  # type: ignore

    from . import _cpython_bypass
    from ._cpython_bypass import enum_compat

    for mod in _cpython_bypass._bypassed_modules_:
        sys.modules[mod] = _cpython_bypass

    def warn(msg: str) -> None:
        print("WARNING: {msg}")

    from ._cpython_bypass import Generic as GenericABC  # type: ignore[attr-defined, misc]


else:
    raise NotImplementedError(
        "tg_gui (and tg_gui.core) does not currently support the "
        + f"{repr(sys.implementation.name)} python implementation"
    )
