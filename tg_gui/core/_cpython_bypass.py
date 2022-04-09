# ---- shared ----
import builtins


class _GetItemBypass:
    def __init__(self, name: str, value: object) -> None:
        self._name = name
        self._value = value

    def __getitem__(self, *_, **__):
        return self._value


# ---- module: __future__ ----
annotations = None


# ---- module: typing ----

TYPE_CHECKING = False

# TODO: make this accept any number of index args
Generic = _GetItemBypass("Generic", object)

TypeVar = lambda *_, **__: None

overload = lambda fn: (
    None
    if __debug__
    else lambda *_, **__: _raise(
        SyntaxError(
            f"overloaded only function defined, "
            + f"{fn.__globals__['__name__']}.{fn.__name__} is not defined without overloads"
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
# enum, auto


def auto():
    return None


def enum_compat(cls):
    raise NotImplementedError


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


# ---- misc ----
# list of all modules this file replaces
_bypassed_modules_ = (
    "__future__",
    "typing",
    "types",
    "enum",
    "abc",
)
