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

import builtins

from ._shared import ConstantGroup, isoncircuitpython
from .base import Widget, LazyInheritedAttribute, NestingError, InheritedAttribute
from .specifiers import SpecifierReference, AttributeSpecifier

# TODO: add app SpecifierReference("app", _find_app_widget)


if not isoncircuitpython():
    from typing import Type, Union, TypeVar, Generic, Callable
    from .specifiers import AttrSpec

else:
    from .typing_bypass import Type, Union, TypeVar, Generic, Callable  # type: ignore


def _search_traverse_up(
    attr_spec: AttrSpec,
    widget: Widget,
    foundit: Callable[["Widget"], bool],
    debug_name: str,
):
    assert isinstance(widget, Widget)
    container = widget if isinstance(widget, Widget) else widget._superior_
    while not foundit(container):
        prev = container
        container = container._superior_
        if container is None:
            raise NestingError(
                f"unable to find outer {debug_name} that {widget} is used in"
            )
    return container


# --- tg-gui builtin specifiers  ---

self = SpecifierReference("self", _search_traverse_up, check=lambda c: c._declarable_)
# app = SpecifierReference("app")

# optimization for for ._superior_ up the widget tree
superior = self._superior_ = AttributeSpecifier(self, "_superior_")  # type: ignore

app = SpecifierReference(
    "app",
    _search_traverse_up,
    check=lambda c: c._is_app_,
)

# a mapping of what specifiers should be avaible in a container's
# class body for constructin sub widgets
_bulitin_tg_specifiers_ = {
    "self": self,
    "superior": superior,
    "app": app,
}

# --- metaclass scopeing for specifiers ---
# will inject a metaclass into

# provide a dict to unpack into the
_continer_meta_kwarg = {}
if not isoncircuitpython():

    class _ContainerScopeingMeta(type):
        def __prepare__(*_, **__) -> dict[str, object]:  # type: ignore
            global _bulitin_tg_specifiers_
            return dict(_bulitin_tg_specifiers_)

    _continer_meta_kwarg["metaclass"] = _ContainerScopeingMeta


# --- class tagging tools ---
def declarable(cls: Type["Widget"]) -> Type["Widget"]:
    """
    dcecorator to mark that a contianer is declarable (like layout or Pages).
    this is used for attr_specs to finf the referenced self in `self.blah`
    """
    assert isinstance(cls, type), f"can only decorate classes"
    assert issubclass(
        cls, Widget
    ), f"{cls} does not subclass Container, it must to be @declarable"
    cls._declarable_ = True
    return cls


def isdeclarable(obj: object) -> bool:
    assert isinstance(obj, type) and issubclass(obj, Widget), (
        "can only test sublcasses of the Widget class" + ", got type {obj}"
    )

    return (
        isinstance(obj, type)
        and issubclass(obj, Widget)
        and hasattr(obj, "_declarable_")
        and obj._declarable_  # type: ignore
    )


# --- the nity gritty ---
class Container(Widget, **_continer_meta_kwarg):
    _nested_: list[Widget]

    _declarable_: bool = False

    _theme_: InheritedAttribute[Theme] = LazyInheritedAttribute("_theme_", None)  # type: ignore

    def __init__(self):
        global Widget

        super().__init__(margin=0)

        self._theme_ = None
        self._nested_ = []

    def _on_nest_(self):
        super()._on_nest_()

    def _nest_(self, widget: Widget):
        if widget not in self._nested_:
            self._nested_.append(widget)
            widget._nest_in_(self)

    def _unnest_(self, widget: Widget):
        if widget in self._nested_:
            widget._unnest_from_(self)
        while widget in self._nested_:
            self._nested_.remove(widget)

    def _build_(self, dim_spec):
        raise NotImplementedError(
            f"{type(self).__name__}._build_(...) not implemented,"
            + " see tg_gui_core/container.py for the template"
        )
        # Template:
        # container subcless specific form code here
        super(Container, self)._build_(dim_spec)
        self._screen_.on_container_build(self)  # platform tie-in

    def _demolish_(self):
        for widget in self._nested_:
            if widget.isformed():
                widget._deform_()
        super()._demolish_()
        self._screen_.on_container_demolish(self)  # platform tie-in

    def _place_(self, pos_spec):
        raise NotImplementedError(
            f"{type(self).__name__}._place_(...) not implemented,"
            + " see tg_gui_core/container.py for the template"
        )
        # Template:
        super(Container, self)._place_(pos_spec)
        # container subcless specific place code here
        self._screen_.on_container_place(self)  # platform tie-in

    def _pickup_(self):
        for widget in self._nested_:
            if widget.isplaced():
                widget._pickup_()
        super()._deform_()
        self._screen_.on_container_pickup(self)  # platform tie-in

    def _show_(self):
        # is this exception needed?
        # raise NotImplementedError(
        #     f"{type(self).__name__}._show_() not implemented,"
        #     + " see tg_gui_core/container.py for the template"
        # )
        # Tempalte:
        super(Widget, self)._show_()
        for wid in self._nested_:
            wid._show_()
        self._screen_.on_container_show(self)

    def _hide_(self):
        for widget in self._nested_:
            if widget.isshowing():
                widget._hide_()
        super()._hide_()
        self._screen_.on_container_hide(self)

    # TODO: fix __del__
    # def __del__(self):
    #     nested = self._nested_
    #     while len(nested):
    #         del nested[0]
    #     super().__del__()

    def _print_tree(self, _level=0, **kwargs):
        super()._print_tree(_level=_level, **kwargs)
        _level += 1
        for wid in self._nested_:
            wid._print_tree(_level=_level, **kwargs)
