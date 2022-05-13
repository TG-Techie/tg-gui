# ---- shared ----
import sys

# ---- module: types ----
@type
def FunctionType():
    pass


LambdaType = type(lambda: None)

BuiltinFunctionType = type(print)

ModuleType = type(sys)


# ---- module: enum ----
# enum, auto, Enum


def auto():
    return None


class Enum:
    def __init__(self, name: str, value: object):
        self.value = value
        self.name = name


def enum_compat(cls: type):
    for k, v in cls.__dict__.items():
        setattr(cls, k, cls(k, v))


# ---- module: abc ----
# ABC, abstractmethod, abstractproperty


class ABC:
    pass


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


# ---- misc ----
# list of all modules this file replaces
__bypassed_modules__ = (
    "types",
    "enum",
    "abc",
)


def load_bypassed_modules():
    this_module = sys.modules[__name__]
    for mod in __bypassed_modules__:
        sys.modules[mod] = this_module
