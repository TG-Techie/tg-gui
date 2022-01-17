from abc import ABC


class Base(ABC):
    name: str


class Derived(Base):
    pass


d = Derived()  # does not error, should (ie not desired behavior)
d.name
