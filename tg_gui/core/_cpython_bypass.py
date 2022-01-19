# shared
import builtins


class _GetItemBypass:
    def __init__(self, name: str, value: object) -> None:
        self._name = name
        self._value = value

    def __getitem__(self, *_, **__):
        return self._value


# module: __future__
annotations = None


# module: typing

TYPE_CHECKING = False

# TODO: make this accept any number of index args
Generic = _GetItemBypass("Generic", object)

TypeVar = lambda *_, **__: None

# module: types
@type
def FunctionType():
    pass


LambdaType = type(lambda: None)

BuiltinFunctionType = type(print)

ModuleType = type(builtins)

Any = object

# module: enum
# enum, auto


def auto():
    return None


def enum_compat(cls):
    raise NotImplementedError


# module: abc:
# ABC, abstractmethod, abstractproperty

ABC = object
if __debug__:

    def _raise(e: Exception) -> None:
        raise e

    abstractmethod = lambda fn: (
        lambda *_, **__: _raise(
            NotImplementedError(
                f"{fn.__globals__['__name__']}.<class>.{fn.__name__}(...) not implemented"
            )
        )
    )

    abstractproperty = lambda fn: property(abstractmethod(fn))

else:
    abstractmethod = lambda fn: fn
    abstractproperty = lambda fn: property(fn)

_bypassed_modules_ = (
    "__future__",
    "typing",
    "types",
    "enum",
    "abc",
)
