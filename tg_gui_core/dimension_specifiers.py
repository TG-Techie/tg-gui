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

# TODO: consider making dim_specs subclasses of spcifiers

from __future__ import annotations

from ._platform_support import enum_compat, use_typing
from enum import Enum, auto

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from .base import Widget

if use_typing() or TYPE_CHECKING:
    DimSpec = Union[
        "DimensionSpecifier",
        tuple[
            Union[int, "DimensionSpecifier"],
            Union[int, "DimensionSpecifier"],
        ],
    ]


def _dimspecify(value: int | DimensionSpecifier, ref: Widget) -> int:
    if isinstance(value, DimensionSpecifier):
        value = value._calc_dim_(ref)
    return value


@enum_compat
class _operations(Enum):
    add = auto()
    sub = auto()
    rsub = auto()
    mul = auto()
    floordiv = auto()


class DimensionSpecifier:
    def _calc_dim_(
        self, inst: Widget
    ) -> tuple[int | "DimensionSpecifier", int | "DimensionSpecifier"]:
        raise NotImplementedError("cannot use a bare DimensionSpecifier")


# maually inline this
def _op_fn(operator):
    # used to define the dunder methods in the DimensionExpression
    def _op_fn_(self, other):
        op = (operator, other)
        return DimensionExpression(
            self._operation_sequence + (op,),
            is_horizontal=self._is_horizontal,
        )

    return _op_fn_


class DimensionExpression:

    operations = _operations

    def __init__(self, operations, *, is_horizontal):
        self._is_horizontal = is_horizontal
        self._operation_sequence = operations

    def __repr__(self):
        dimension = "width" if self._is_horizontal else "height"
        return f"<DimensionExpression:{dimension} {id(self)}>"

    __floordiv__ = _op_fn(_operations.floordiv)

    __add__ = _op_fn(_operations.add)
    __radd__ = _op_fn(_operations.add)

    __mul__ = _op_fn(_operations.mul)
    __rmul__ = _op_fn(_operations.mul)

    __sub__ = _op_fn(_operations.sub)
    __rsub__ = _op_fn(_operations.rsub)

    def _calc_dim(self, dims: tuple[int, int]) -> int:
        ops = _operations
        running_value = dims[0] if self._is_horizontal else dims[1]
        for op, value in self._operation_sequence:
            # if it is also a DimExpr, simplify it
            if isinstance(value, DimensionExpression):
                value = value._calc_dim(dims)
            elif isinstance(value, DimensionExpressionConstructor):
                value = dims[0] if value._is_horizontal else dims[1]
            assert isinstance(value, int), f"found `{repr(value)}`"
            # apply the operation
            if op is ops.floordiv:
                running_value //= value
            elif op is ops.mul:
                running_value *= value
            elif op is ops.add:
                running_value += value
            elif op is ops.sub:
                running_value -= value
            elif op is ops.rsub:
                running_value = value - running_value
            else:
                raise ValueError(f"unknown operator {repr(op)}")
        else:
            return running_value


# maually inline this
def _op_constr_fn(operator):
    def _op_constr_fn_(self: DimensionExpressionConstructor, value: int):
        op = (operator, value)
        return DimensionExpression((op,), is_horizontal=self._is_horizontal)

    return _op_constr_fn_


class DimensionExpressionConstructor:
    def __init__(self, *, name: str, is_horizontal: bool):
        self._name = name
        self._is_horizontal = is_horizontal

    def __repr__(self):
        return f"<DimensionExpressionConstructor '{self._name}'>"

    __floordiv__ = _op_constr_fn(_operations.floordiv)

    __add__ = _op_constr_fn(_operations.add)
    __radd__ = _op_constr_fn(_operations.add)

    __mul__ = _op_constr_fn(_operations.mul)
    __rmul__ = _op_constr_fn(_operations.mul)

    __sub__ = _op_constr_fn(_operations.sub)
    __rsub__ = _op_constr_fn(_operations.rsub)


# for import
class ratio(DimensionSpecifier):
    def __init__(self, expr):
        self._base_expr = expr

    def _calc_dim_(self, inst):
        return self._base_expr._calc_dim(inst._phys_size_)


height = DimensionExpressionConstructor(
    name="height",
    is_horizontal=False,
)

width = DimensionExpressionConstructor(
    name="width",
    is_horizontal=True,
)
