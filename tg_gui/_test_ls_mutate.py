from .liststate import *

the_source = [1, 2, 3]
lsstate = ListState(the_source)


class Foo:

    x = lsstate

    def __init__(self) -> None:

        self._id_ = uid()

        print("__init__():", Foo.x._change_guard, Foo.x._change_nesting)

        assert self.x is lsstate
        self.x._register_handler_(self, lambda: print(f"changed! {self.x}"))

    @changes(x)
    def foo(self):

        print("foo():", Foo.x._change_guard, Foo.x._change_nesting)

        assert self.x is the_source


print("starting state", Foo.x._change_guard, Foo.x._change_nesting)

f = Foo()

assert Foo.x is lsstate
assert f.x is lsstate

print("pre foo", Foo.x._change_guard, Foo.x._change_nesting)

f.foo()

print("post foo", Foo.x._change_guard, Foo.x._change_nesting)

with lsstate as lsx:
    assert lsx == the_source
    print(lsstate)
    print("in with:", Foo.x._change_guard, Foo.x._change_nesting)

print("ending:", Foo.x._change_guard, Foo.x._change_nesting)

print("passed")
