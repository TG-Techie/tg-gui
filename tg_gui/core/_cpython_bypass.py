# shared
import builtins

# module: __future__
annotations = None


# module: typing

TYPE_CHECKING = False

# TODO: make this accept any number of index args
Generic = {None: object}

TypeVar = lambda *_, **__: None

# module: types
@type
def FunctionType():
    pass


LambdaType = type(lambda: None)

BuiltinFunctionType = type(print)

ModuleType = type(builtins)

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
