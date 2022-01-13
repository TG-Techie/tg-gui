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

from .base import Widget
from .dimension_specifiers import DimensionSpecifier
from .stateful import State

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, Any, Tuple  # Manual import to avoid Container Conflic

    AttrSpec = Tuple[str, ...]

    from .container import Container

    ResolveCheck = Callable[[Widget], bool]

    Resolver = Callable[
        [AttrSpec, Widget, ResolveCheck, str],
        Any,
    ]


class SpecifierReference:
    def __init__(
        self,
        name: str,
        resolver: Resolver,
        check: Callable[[Widget], bool],
    ):
        self._name = name
        self._resolver = resolver
        self._check = check

    def __repr__(self) -> str:
        return f"<{type(self).__name__} '{self._name}'>"

    def __getattr__(self, name: str) -> "AttributeSpecifier":
        if name.startswith("_") != name.endswith("_"):
            raise AttributeError(f"cannot specify private atrributes, found .{name}")
        return AttributeSpecifier(self, (name,))

    def _resolve_reference_(self, attr_spec: AttrSpec, ref: Widget):
        return self._resolver(attr_spec, ref, self._check, self._name)


def specify(spec, ref):
    if isinstance(spec, Specifier):
        return spec._resolve_specified_(ref)
    elif isinstance(spec, DimensionSpecifier):
        return spec._calc_dim_(ref)
    else:
        return spec
    # return spec._resolve_specified_(ref) if isinstance(spec, Specifier) else spec


class Specifier:  # protocol
    def _resolve_specified_(self, _):
        raise NotImplementedError

    def _code_str_(self):
        raise NotImplementedError

    def __str__(self):
        return self._code_str_()

    def __repr__(self):
        type(self).__name__
        self._code_str_()
        return f"<{type(self).__name__}: `{self._code_str_()}`>"


class AttributeSpecifier(Specifier):
    _not_present_sentinel = object()

    def _code_str_(self):
        return f"{self._spec_ref._name}.{'.'.join(self._attr_path)}"

    def __init__(self, spec_ref, attr_path):
        if isinstance(attr_path, str):
            attr_path = (attr_path,)
        assert isinstance(attr_path, tuple), f"found {attr_path}, expected tuple"
        assert isinstance(
            spec_ref, SpecifierReference
        ), f"found {attr_path}, expected SpecifierReference"
        self._attr_path = attr_path
        self._spec_ref = spec_ref

    def __getattr__(self, name):
        assert name.startswith("_") == name.endswith(
            "_"
        ), f"cannot specify private atrributes, found .{name}"
        return AttributeSpecifier(
            self._spec_ref,
            self._attr_path + (name,),
        )

    def __call__(self, *args, **kwargs):
        return ForwardMethodCall(self, args, kwargs)

    def _resolve_specified_(self, ref: Widget):
        attr = self._spec_ref._resolve_reference_(self._attr_path, ref)
        missing = self._not_present_sentinel
        for attrname in self._attr_path:
            if (
                clsattr := getattr(type(attr), attrname, missing)
            ) is not missing and isinstance(clsattr, State):
                return clsattr
            else:
                attr = getattr(attr, attrname)
        return attr

    def _set_specified_(self, *_, **__):
        raise NotImplementedError


class ForwardMethodCall(Specifier):
    def __init__(self, method_spec, args, kwargs):
        assert isinstance(method_spec, AttributeSpecifier)
        self._method_spec = method_spec
        self._args = args
        self._kwargs = kwargs
        self._code_str = None

    def _code_str_(self):
        if self._code_str is None:
            args = tuple(str(arg) for arg in self._args)
            kwargs = tuple(f"{kw}={str(arg)}" for kw, arg in self._kwargs.items())

            self._code_str = (
                f"{self._method_spec._code_str_()}({', '.join(args+kwargs)})"
            )
        return self._code_str

    def _resolve_specified_(self, ref):
        # find method
        method = self._method_spec._resolve_specified_(ref)
        # assemble args and kwargs if they are specifiers
        # these will be re-used so are not interators
        args = tuple(specify(arg, ref) for arg in self._args)
        kwargs = {kw: specify(arg, ref) for kw, arg in self._kwargs.items()}
        return lambda: method(*args, **kwargs)
