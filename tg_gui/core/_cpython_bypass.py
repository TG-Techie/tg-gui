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


_bypassed_modules_ = (
    "__future__",
    "typing",
    "types",
    "enum",
    "abc",
)
