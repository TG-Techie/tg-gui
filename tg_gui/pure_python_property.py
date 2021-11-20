try:
    from typing import *
except:
    pass


class property:

    fget: Callable[[object], Any] | None
    fset: Callable[[object, object], None] | None

    def __init__(
        self,
        fget: Callable[[object], Any] | None = None,
        fset: Callable[[object, object], None] | None = None,
    ):
        self.fget = fget
        self.fset = fset

        if fget is not None and hasattr(fget, "__name__"):
            self._name = fget.__name__
        elif fset is not None and hasattr(fset, "__name__"):
            self._name = fset.__name__
        else:
            self._name = "<unnamed property>"

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError(f"attribute .{self._name} is unreadbale")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError(f"can't set attribute .{self._name}")
        self.fset(obj, value)

    def getter(self, fget: Callable[[object], Any]) -> "property":
        return type(self)(fget, self.fset)

    def setter(self, fset: Callable[[object, object], None]) -> "property":
        return type(self)(self.fget, fset)

    # circuitpython compatiblity guard (for future features)
    __set_name__ = object()
