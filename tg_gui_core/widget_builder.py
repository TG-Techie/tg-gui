# The MIT License (MIT)
#
# Copyright (c) 2022 Jonah Yolles-Murphy (TG-Techie)
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

from ._implementation_support import isoncpython, isoncircuitpython
from .base import UID, uid, Widget, _MISSING
from .container import Container
from .stateful import State

from typing import TYPE_CHECKING, TypeVar, Generic
from types import FunctionType, MethodType

_W = TypeVar("_W", bound=Widget)
_C = TypeVar("_C", bound=Container)

if TYPE_CHECKING:
    from typing import Callable, Type, Any, ClassVar

    from .position_specifiers import PosSpec
    from .dimension_specifiers import DimSpec


class BuildError(RuntimeError):
    pass


def _widget_builder_cls_format(cls: Type[Container]) -> Type[Container]:
    """
    scan throguht a class body to find sugary widget builders (no argument lamdas)
    and wrap them in WigetBuiilder descriptors.
    """
    for name in dir(cls):
        attr = getattr(cls, name)
        builder = None
        if isinstance(attr, FunctionType) and attr.__name__ == "<lambda>":
            builder = WidgetBuilder(attr)
            setattr(cls, name, builder)
        elif isinstance(attr, WidgetBuilder):
            builder = attr
        else:
            pass

        # circuitpython does not support __set_name__, so add it in manually
        if isoncircuitpython() and builder is not None and builder.name is None:
            builder.__set_name__(name, cls)

    return cls


class ForwardMethodCall:
    def __init__(
        self,
        boundmethod: MethodType,
        func: FunctionType,
        *,
        attrname: str,
        clsname: str,
    ) -> None:

        self._func: FunctionType = func
        self._boundmethod: MethodType = boundmethod

        self._attrname: str = attrname
        self._clsname: str = clsname
        self._called: bool = False
        self._build_closed: bool = False

        if isoncpython():
            assert (
                boundmethod.__func__ is func
            ), f"error in args {self}, {boundmethod}.__func__ != {func}"

    def _close_build_(self):
        # make sure the method is called at least once
        if not self._called:
            self._raised_not_called()

        self._build_closed = True
        self._func = None  # type: ignore
        self._boundmethod = None  # type: ignore

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        # guard against not being called or being called once but not other times
        if self._build_closed:
            self._raise_not_called()

        mthd = self._boundmethod
        if len(args) == 0 and len(kwargs) == 0:
            self._called = True
            return mthd
        else:
            # return a lambda that does not capture a closure
            self._called = True
            return lambda *, __fn=mthd, __ar=args, __kw=kwargs: __fn(*__ar, **__kw)

    def _raised_not_called(self):
        raise BuildError(
            "methods must be called explicitly in widget builders. "
            + f"found `self.{self._attrname}` in "
            + f"`class {self._clsname}(...): {self._attrname} = lamdba: ...`, "
            + f"must use `self.{self._attrname}(...)`"
        )


class _BuildProxy(Generic[_W]):
    def __init__(self, proxied: _W, _debug: str | None = None) -> None:
        self._widget: _W = proxied
        self._cache: dict[str, Any] = {}
        self._debug: str = _debug or ""

    def close_build(self):
        # close any build objects
        for buildattr in self._cache.values():
            if hasattr(buildattr, "_close_build_"):
                buildattr._close_build_()
        else:
            self._cache.clear()

    def __getattr__(self, name: str) -> Any:

        widget = self._widget
        cache = self._cache

        ownercls = type(widget)

        if name in cache:
            return cache[name]

        clsattr = getattr(ownercls, name, _MISSING)

        if isinstance(clsattr, State):
            return clsattr

        instattr = getattr(widget, name, _MISSING)

        if isinstance(instattr, MethodType):
            assert isinstance(
                clsattr, FunctionType
            ), f"{self} w/ owner {widget} of type {ownercls} conflicitng types for bound method and cls attribute"
            returnvalue = ForwardMethodCall(
                instattr, clsattr, attrname=name, clsname=ownercls.__name__
            )

        else:
            # TODO: formalize this?
            print(
                f"fallthrough: `{widget}.{name}` featched by {self} with value "
                + f"{instattr} (clsattr={clsattr} w/ obj as missing)"
            )
            returnvalue = instattr
            # assert False, "unreachable"

        # cache and return
        assert name not in cache
        cache[name] = returnvalue
        return returnvalue

    @classmethod
    def decalred_proxy_from(cls, widget: Widget) -> _BuildProxy:
        # climb up the widget tree to find the nearest declared widget
        if isinstance(widget, Container) and widget._declarable_:
            return cls(widget)
        superior = widget._superior_
        while superior is not None:
            if superior._declarable_:
                superior = superior._superior_
            else:
                return cls(superior)
                # proxy = getattr(superior, "_declared_proxy_", None)
                # if proxy is None:
                #     proxy = cls(superior)
                # superior._declared_proxy_ = proxy
                # return proxy
        else:
            raise BuildError(f"could not find superior decalred widget above {widget}")

    @classmethod
    def app_proxy_from(cls, widget: Widget) -> _BuildProxy:
        # climb up the widget tree to find the nearest declared widget
        if isinstance(widget, Container) and widget._is_app_:
            return cls(widget)
        superior = widget._superior_
        while superior is not None:
            if not superior._is_app_:
                superior = superior._superior_
            else:
                return cls(superior)
                # proxy = getattr(superior, "_app_proxy_", None)
                # if proxy is None:
                #     proxy = cls(superior)
                # superior._app_proxy_ = proxy
                # return proxy
        else:
            raise BuildError(f"could not find superior app widget above {widget}")


class WidgetBuilder(Generic[_C, _W]):
    """
    This is used to manage linking state, method forward method calls, and attributes.
    It acts as a descriptor around a lambda that takes no arguments but references `self`
    EX:
    ```
    @layoutclass
    class SingleCounter(View):

        sharedcount = State(0) # singel state shared by all instances

        def __init__(self, incby: int):
            self._incby = incby

        body = lambda: VStack(
            Label(self.sharedcount >> str),
            Button(f"inc + {self._incby}", self.inc(self._incby))
        )

        def inc(self) -> None:
            self.sharedcount += 1
    ```
    """

    def __init__(self, fn: Callable[[], _W]) -> None:

        self._id_: UID = uid()
        self._fn: Callable[[], _W] = fn
        self._bodycls: Type[_C] | None = None

        # TODO: add better type and name checking
        assert fn.__name__ == "<lambda>", f"{self} fn must be a lambda"
        # TODO: use inspect to check the signature on cpython

        # set in __set_name__
        self.name: str | None = None
        self.bodycls: Type[_C] | None = None

    def __set_name__(self, bodycls: Type[_C], name: str) -> None:
        """
        This is called when the class is defined.
        on circuitpython this has to be called by a class decorator
        """
        assert self.name is None, f"{self} name already set to {self.name}"
        assert self.bodycls is None, f"{self} bodycls already set to {self.bodycls}"
        self.name = name
        self.bodycls = bodycls

    def __repr__(self) -> str:
        if self.name is None:
            return f"<{type(self).__name__}: {self._id_} {{no name set}}>"
        else:
            return f"<{type(self).__name__}: {self._id_} {self.cntrcls.__name__}.{self.name}>"

    def __get__(
        self, owner: _C, ownercls: Type[_C]
    ) -> Callable[[PosSpec, DimSpec], _W]:
        """
        when the descriptor is accessed, it returns a function that takes the position
        specifier and dimension specifier that builds the widget.
        """
        if owner is None:
            return self  # type: ignore

        # return a function that takes no args and does not caputre a closure
        return lambda *, __build=self.build, __owner=owner: __build(__owner)

    def build(self, owner: _C) -> _W:

        # get the proxy objects for the build process to use
        # however, if the owner has them cached, use thos isead of making new proxies
        declared_proxy = _BuildProxy.decalred_proxy_from(owner)
        app_proxy = _BuildProxy.app_proxy_from(owner)

        # set internal state and store the self object if (for some reason) it is already set
        scope = self._fn.__globals__
        existsing_self = scope.get("self", _MISSING)
        existsing_app = scope.get("app", _MISSING)

        # inject self as the global self variable
        scope["self"] = declared_proxy
        scope["app"] = app_proxy

        widget = self._fn()

        # retsore the self object if it was set and unlock self
        if existsing_self is not _MISSING:
            scope["self"] = existsing_self
        if existsing_app is not _MISSING:
            scope["app"] = existsing_app

        declared_proxy.close_build()
        app_proxy.close_build()

        del declared_proxy
        del app_proxy

        return widget


class Declarable(Container):
    _declarable_: ClassVar[bool] = True

    @classmethod
    def _subclass_format_(cls: Type[Declarable], subcls: Type[Declarable]) -> str:
        _widget_builder_cls_format(subcls)
