class Enum:
    def __new__(cls, *_, **__):
        raise TypeError(
            f"Cannot make Enum '{cls.__name__}' instances on circuitpython, "
            "decorate the class with @enum_compat"
        )

    def __init__(self, name: str, autoid: int):
        self._name: str = name
        # self._outer: Type[Enum] = outer
        self._vrnt_id = autoid

    def __eq__(self, other):
        return (
            self._vrnt_id == other._vrnt_id if isinstance(other, type(self)) else False
        )

    def __hash__(self):
        return hash(repr(self)) ^ hash(self._vrnt_id)

    def __repr__(self):
        return f"<{type(self).__name__}.{self._name}: {self._vrnt_id}>"


auto = lambda: None


def enum_compat(cls: Type[Enum]):

    assert issubclass(cls, Enum)

    cls.__new__ = lambda cls, name: object.__new__(cls)  # type: ignore

    autoid = 0
    for name in dir(cls):
        attr = getattr(cls, name)

        if name.startswith("__") or callable(attr):
            continue

        autoid += 1
        setattr(cls, name, cls(name, autoid))

    cls.__new__ = Enum.__new__  # type: ignore
    cls.__init__ = None

    return cls
