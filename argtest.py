from tg_gui import *

from typing import TYPE_CHECKING


@widget
class Foo(Widget):
    _build_ = _place_ = _pickup_ = _demolish_ = _native_ = lambda *_, **__: None  # type: ignore[assignment]

    bld1: int = buildattr(repr=True)
    thm1: str = themedattr(default="kw1", repr=True)


print(Foo, set(Foo._initkwargs_))
print(f1 := Foo(bld1=1))
print(f2 := Foo(bld1=2, thm1="*2"))


@widget
class Bar(Foo):
    def __init__(self, bld1: int, **kwargs):
        super().__init__(bld1=bld1, **kwargs)


print(Bar, set(Bar._initkwargs_))
print(bld2 := Bar(1))
print(thm1 := Bar(1, thm1=2))


@widget
class Bad(Foo):
    # this should be lint checked
    def __init__(self, bldx: int, **kwargs):
        super().__init__(bld1=bldx, **kwargs)
