# ---- shared ----
import sys

import builtins

try:
    from typing import Any
except ImportError:
    pass
else:
    assert (
        False
    ), f"the {__name__} module should not be imported except when on circuitpython"


class GetItemBypass:
    def __init__(self, name: str, value: Any) -> None:
        self._name = name
        self._value = value

    def __getitem__(self, *_, **__):
        return self._value

    def __call__(self, *args, **kwds):
        return self._value(args, kwds)

    def __getattr__(self, name: str):
        return getattr(self._value, name)

    def __isinstance_hook__(self, inst):
        return isinstance(inst, self._value) or (
            hasattr(self._value, "__cp_compat_instancecheck__")
            and self._value.__cp_compat_instancecheck__(inst)
        )


# ---- module: typing ----

TYPE_CHECKING = False

# TODO: make this accept any number of index args


def Generic__new__(cls, *args, **kwds):
    assert getattr(
        cls, "__generirc_compat__", False
    ), f"generic class {cls} not decorated with @generic_compat"
    return object.__new__(cls)


Generic = GetItemBypass(
    "Generic", type("Generic", (object,), {"__new__": Generic__new__})
)

TypeVar = lambda *_, **__: None

overload = (
    lambda fn: None
    if __debug__
    else lambda fn: (
        lambda *_, **__: _raise(
            SyntaxError(
                f"overloaded only function defined, "
                + f"{fn.__globals__['__name__']}.{fn.__name__} is not defined without overloads"
            )
        )
    )
)

# ---- module: types ----
@type
def FunctionType():
    pass


LambdaType = type(lambda: None)

BuiltinFunctionType = type(print)

ModuleType = type(builtins)

Any = object

# ---- module: enum ----
# enum, auto, Enum


def auto():
    return None


def enum_compat(cls):
    cls.__dict__.update({k: cls(v) for k, v in cls.__dict__.items()})


class Enum:
    def __init__(self, value):
        self.value = value


# ---- module: abc ----
# ABC, abstractmethod, abstractproperty

ABC = object
if __debug__:

    def _raise(e: Exception) -> None:
        raise e

    abstractmethod = lambda fn, *_, **__: (
        lambda *_, **__: _raise(
            NotImplementedError(
                f"{fn.__globals__['__name__']}.<class>.{fn.__name__}(...) not implemented"
            )
        )
    )

    abstractclassmethod = lambda fn, *_, **__: classmethod(abstractmethod(fn))
    abstractproperty = lambda fget, *_, **__: property(abstractmethod(fget))

else:
    abstractmethod = lambda fn: fn  # type: ignore[misc, assignment]
    abstractclassmethod = classmethod  # type: ignore[assignment]
    abstractproperty = property  # type: ignore[assignment]

# ---- module: __future__ ----
annotations = None

# ---- misc ----
# list of all modules this file replaces
__bypassed_modules__ = (
    "__future__",  # added in CP 7 ?
    "typing",
    "types",
    "enum",
    "abc",
)


def load_bypassed_modules():
    this_module = sys.modules[__name__]
    for mod in __bypassed_modules__:
        sys.modules[mod] = this_module
