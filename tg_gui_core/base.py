# The MIT License (MIT)
#
# Copyright (c) 2021 Jonah Yolles-Murphy (TG-Techie)
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from __future__ import annotations

from ._shared import *
from .position_specifiers import *
from .dimension_specifiers import *


if not isoncircuitpython():
    from typing import Protocol, Union, TypeVar, Generic, Any, Callable, NoReturn

    if isoncircuitpython():  # hack for circular typing import
        from .root_widget import Root
        from .container import Widget

else:
    from .typing_bypass import Protocol, Union, TypeVar, Generic, Any, Callable  # type: ignore

# --- type stuff ---
T = TypeVar("T")

InheritedAttribute = Union[
    None,
    T,
    "LazyInheritedAttribute[Union[T, None]]",
]

# --- Exception ("oh crap") types ---


class NestingError(RuntimeError):
    pass


class PlacementError(RuntimeError):
    pass


class RenderError(RuntimeError):
    pass


def singleinstance(cls):
    return cls()


def application(cls):
    cls._is_app_ = True
    return cls()


class LazyInheritedAttribute(Generic[T]):
    def __init__(self, attrname: str, initial: T) -> None:
        # TODO: add doc string to decribe the funcitonality
        self._attrname = attrname
        self._priv_attrname = "_inherited_" + attrname + "_attr_"
        self._initial = initial

    def __repr__(self):
        return f"<InheritedAttribute: .{self._attrname}>"

    def __get__(self, owner: "Widget", ownertype: Type[object]) -> T:
        privname = self._priv_attrname
        assert hasattr(owner, privname), (
            f"`{owner}.{self._attrname}` attribute not initialized, "
            + f"inherited `{type(owner).__name__}.{self._attrname}` attributes must be "
            + f"initialized to the inital `{self._initial}` or some other value"
        )
        privattr = getattr(owner, privname)
        if privattr is not self._initial:  # normal get behavior
            return privattr
        else:  # get the inherited attribute
            heirattr = getattr(owner._superior_, self._attrname)
            if heirattr is not self._initial:
                setattr(owner, privname, heirattr)
            return heirattr

    def __set__(self, owner, value) -> None:
        setattr(owner, self._priv_attrname, value)


Color = int


class color(Color):
    # TODO: consider make ready only using proerties and lambdas vs performance
    _clear = None  # tentative
    red = 0xFF0000
    orange = 0xFFA500
    yellow = 0xFFFF00
    green = 0x00FF00
    lightgreen = 0xA0FFA0
    blue = 0x0000FF
    purple = 0xCC8899

    white = 0xFFFFFF
    lightgray = 0xC4C4C4
    gray = 0x909090
    darkgray = 0x606060
    black = 0x000000

    def fromfloats(r, g, b):
        r = round(255 * r ** 1.125)
        g = round(255 * g ** 1.125)
        b = round(255 * b ** 1.125)
        return (r << 16) | (g << 8) | (b << 0)


class _Screen_:
    """
    this _Screen_ class provides an interface to tie in platform speific
    functionality.
    """

    _root: None | Root
    default_margin: int
    _id_: int

    def __init__(self, default_margin=5):
        self._id_ = uid()
        self._root = None
        self.default_margin = default_margin

    def run(self) -> NoReturn:
        raise NotImplementedError()

    # Not strictly necesary, meant to make debugging easier
    @property
    def root(self) -> Root:
        if self._root is not None:
            return self._root
        else:
            raise AttributeError(f"{self}._root_ not initialized, needs to be assigned")

    @root.setter
    def root(self, value):
        if self._root is None:
            self._root = value
            self.on_root_set(value)
        else:
            raise AttributeError(f"{self}._root_ already initialized")

    def __repr__(self):
        return f"<{type(self).__name__} {self._id_}>"

    def on_root_set(self, root):
        pass

    # platform tie-in functions

    def on_widget_nest_in(_, widget: "Widget"):
        raise NotImplementedError

    def on_widget_unnest_from(_, widget: "Widget"):
        raise NotImplementedError

    def on_widget_build(_, widget: "Widget"):
        raise NotImplementedError

    def on_widget_demolish(_, widget: "Widget"):
        raise NotImplementedError

    def on_widget_place(_, widget: "Widget"):
        raise NotImplementedError

    def on_widget_pickup(_, widget: "Widget"):
        raise NotImplementedError

    def on_widget_show(_, widget: "Widget"):
        raise NotImplementedError

    def on_widget_hide(_, widget: "Widget"):
        raise NotImplementedError

    # container tie-ins

    def on_container_build(_, wid: "Widget"):
        raise NotImplementedError

    def on_container_demolish(_, wid: "Widget"):
        raise NotImplementedError

    def on_container_place(_, widget: "Widget"):
        raise NotImplementedError

    def on_container_pickup(_, widget: "Widget"):
        raise NotImplementedError

    def on_container_show(_, widget: "Widget"):
        raise NotImplementedError

    def on_container_hide(_, widget: "Widget"):
        raise NotImplementedError


class Widget:  # type: ignore
    _id_ = uid()

    _superior_: Widget
    _native_: Any

    _size_: tuple[int, int]
    _phys_size_: tuple[int, int]

    _coord_: tuple[int, int]
    _rel_coord_: tuple[int, int]
    _phys_coord_: tuple[int, int]

    # --- class attr and future work ---
    _screen_: LazyInheritedAttribute[None | _Screen_] = LazyInheritedAttribute(
        "_screen_", None
    )
    _is_app_ = False

    # --- body ---
    def __init__(self, *, margin: int | None = None):
        global Widget
        self._id_ = uid()

        self._superior_ = None
        self._screen_ = None
        self._native_ = None

        self._size_ = None  # type: ignore
        self._phys_size_ = None  # type: ignore

        self._coord_ = None  # type: ignore
        self._rel_coord_ = None  # type: ignore
        self._phys_coord_ = None  # type: ignore

        self._is_shown = False
        self._margin_spec = margin

    dims = property(lambda self: self._size_)
    width = property(lambda self: self._size_[0])
    height = property(lambda self: self._size_[1])

    coord = property(lambda self: self._coord_)
    x = property(lambda self: self._coord_[0])
    y = property(lambda self: self._coord_[1])

    @property
    def _margin_(self) -> int:
        if self._margin_spec is not None:
            margin = self._margin_spec
        else:
            assert self._screen_ is not None
            self._margin_spec = margin = self._screen_.default_margin
        return margin

    # internal protocols
    # ._phys_size_
    # ._size_
    # ._coord_
    # ._rel_coord_
    # ._phys_coord_
    # ._phys_end_coord_

    def isnested(self):
        return self._superior_ is not None

    def isbuilt(self):
        return self._size_ is not None

    def isplaced(self):
        return self._coord_ is not None  # and self.isnested()

    # def isbuilt(self):
    #     return self.isplaced() and self._native_ is not None

    def isshowing(self):
        return self._is_shown

    def __repr__(self):
        return f"<{type(self).__name__} {self._id_}>"

    def __get__(self, owner, ownertype=None):
        """
        Widgets act as their own descriptors, this allows them to auto nest into layouts.
        """
        if not self.isnested():
            owner._nest_(self)
        return self

    def __call__(self, pos_spec, dim_spec):
        self._build_(dim_spec)
        self._place_(pos_spec)
        return self

    def _show_(self):
        assert self.isnested()
        self._is_shown = True
        self._screen_.on_widget_show(self)

    def _hide_(self):
        assert self.isshowing()
        self._is_shown = False
        self._screen_.on_widget_hide(self)

    def _nest_in_(self, superior):
        """
        Called by the superior of a widget (self) to link the widget as it's subordinate.
        """
        # nesting is permanent, this should be called by the parent widget once
        current = self._superior_
        if current is None:

            self._superior_ = superior
            self._screen_ = superior._screen_
            self._screen_.on_widget_nest_in(self)

        elif current is superior:  # if double nesting in same thing
            print(
                f"WARNING: {self} already nested in {current}, "
                + "double nesting in the same widget is not advisable"
            )
        else:
            raise ValueError(
                f"{self} already nested in {current}, " + f"cannot nest in {superior}"
            )

        self._on_nest_()

    def _unnest_from_(self, superior=None):
        """
        Called by superiors to un-link the (now-ex) subordinate from the superior
        """
        if superior is None:
            superior = self._superior_
        if superior is self._superior_:
            # platform tie-in
            self._screen_.on_widget_unnest_from(self)
            # clear out data
            self._screen_ = None
            self._superior_ = None
        else:
            raise RuntimeError(
                f"cannot unnest {self} from {superior}, it is nested in {self._superior_}"
            )

    def _build_(self, dim_spec):
        suggested = self._specify_dim_spec(dim_spec)
        self._build_exactly_(*suggested)

    def _specify_dim_spec(self, dim_spec: Union[tuple[int, int], DimensionSpecifier]):
        # format dims
        if isinstance(dim_spec, DimensionSpecifier):
            spec = dim_spec._calc_dim_(self)
        else:
            spec = dim_spec

        assert isinstance(spec, tuple), f"self={self}, tuple={tuple}"

        width, height = spec
        if isinstance(width, DimensionSpecifier):
            width = width._calc_dim_(self)  # type: ignore
        if isinstance(height, DimensionSpecifier):
            height = height._calc_dim_(self)  # type: ignore

        # TODO: see if these are needed
        assert width == int(width)  # type: ignore
        assert height == int(height)  # type: ignore
        width = int(width)  # type: ignore
        height = int(height)  # type: ignore

        return (width, height)

    def _build_exactly_(self, width, height):
        assert self.isnested(), f"{self} must be nested to size it, it's not"
        assert not self.isbuilt(), f"{self} is already built"

        # margin_spec = self._margin_spec
        # if margin_spec is None:
        #     margin_spec = self._screen_.default_margin

        # if isinstance(margin_spec, DimensionSpecifier):
        #     margin = margin_spec._calc_dim_(self)
        # else:
        #     margin = margin_spec

        # self._margin_ = margin
        margin = self._margin_
        self._size_ = (width, height)
        self._phys_size_ = (width - margin * 2, height - margin * 2)

        self._screen_.on_widget_build(self)  # platform tie-in

    def _demolish_(self):
        self._screen_.on_widget_demolish(self)  # platform tie-in

        self._margin_ = None
        self._size_ = None
        self._phys_size_ = None

    def _place_(self, pos_spec):
        assert self.isbuilt(), f"{self} must be sized to place it, it's not"
        assert not self.isplaced(), f"{self} already placed"

        # format coord
        if isinstance(pos_spec, PositionSpecifier):
            x, y = pos_spec._calc_coord_(self)
        else:
            assert isinstance(pos_spec, tuple)
            x, y = pos_spec

        if isinstance(x, PositionSpecifier):
            x = x._calc_x_(self)
        if isinstance(y, PositionSpecifier):
            y = y._calc_y_(self)

        # for negative numbers adjust to right aligned
        if x < 0:
            x = self._superior_.width - self.width + 1 + x
        if y < 0:
            y = self._superior_.height - self.height + 1 + y

        # calc and store the placements
        margin = self._margin_
        spr_x, spr_y = self._superior_._phys_coord_

        self._coord_ = (x, y)
        self._rel_coord_ = rx, ry = (x + margin, y + margin)
        self._phys_coord_ = px, py = (spr_x + rx, spr_y + ry)

        pw, ph = self._phys_size_
        self._phys_end_coord_ = (px + pw, py + ph)

        self._screen_.on_widget_place(self)  # platform tie-in

    def _pickup_(self):
        assert self.isplaced()
        self._screen_.on_widget_pickup(self)  # platform tie-in
        # only containers need to worry about when to cover vs replace
        self._coord_ = None
        self._rel_coord_ = None
        self._phys_coord_ = None
        self._phys_end_coord_ = None

    def _on_nest_(self):
        pass

    def _on_unnest_(self):
        pass

        # TODO: fix __del__
        # def __del__(self):
        #     # deconstruct from current stage
        #     if self.isshowing():
        #         self._hide_()
        #     if self.isplaced():
        #         self._pickup_()
        #     if self.isbuilt():
        #         self._demolish_()
        #     if self.isnested():
        #         print(self)
        #         self._superior_._unnest_(self)

        # remove double links
        self._superior_ = None
        self._screen_ = None
        # remove placement cache
        self._size_ = None
        self._phys_size_ = None
        self._coord_ = None
        self._rel_coord_ = None
        self._phys_coord_ = None

    def _print_tree(
        self, *, indent="    ", fn: Callable[["Widget"], Any] = lambda _: "", _level=0
    ):
        print(indent * _level, self, fn(self))