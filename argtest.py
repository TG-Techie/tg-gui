from tg_gui import *


@widget
class Foo(Widget):
    _build_ = _place_ = _pickup_ = _demolish_ = _native_ = lambda *_, **__: None

    arg1: BuildAttr[int] = BuildAttr(positional=True, repr=True)
    kw1: ThemedAttr[str] = ThemedAttr(default="kw1", repr=True)


print(Foo, Foo._initargs_, set(Foo._initkwargs_))
print(f1 := Foo(1))
print(f2 := Foo(arg1=1))


@widget
class Bar(Foo):
    arg2: BuildAttr[int] = BuildAttr(positional=True, repr=True)
    kw2: ThemedAttr[str] = ThemedAttr(default="kw2", repr=True)


print(Bar, Bar._initargs_, set(Bar._initkwargs_))
print(b1 := Bar(1, 2))
print(b2 := Bar(1, 2))
