from __future__ import annotations

from ._implementation_support_ import isoncircuitpython
from ._shared_ import uid, UID, Pixels
from ._platform_support_ import Platform, requiredplatformmethod
from .widget import Widget
from .themeing import BuildAttribute, StyleAttribute

from typing import TYPE_CHECKING, TypeVar, Generic
from abc import ABC, abstractmethod, abstractproperty


if TYPE_CHECKING:
    from typing import Type, Any

    from ._platform_support_ import NativeElement, NativeContainer

_T = TypeVar("_T")

# TODO: make this
class State(Generic[_T]):
    def __init__(self) -> None:
        raise NotImplementedError


# --- platform widget ---
# TODO: Rename to PlatformWidget to something cooler (ie clearer and less boring)
class PlatformWidget(Widget):

    # --- widget attributes ---
    _margin_: Pixels = BuildAttribute(default=5)  # type: ignore[assignment]

    def __init__(self, **kwargs):
        self._native_ = None

        self._extract_kwargs(kwargs)

        super().__init__(**kwargs)

    def _extract_kwargs(self, kwargs: dict[str, Any]) -> None:
        # TODO: convert this to use a _subclass_sugar_ silter to extract a list of allowed args
        cls = type(self)
        for key in set(kwargs):
            if isinstance(getattr(cls, key, None), (BuildAttribute, StyledAttribute)):
                setattr(self, key, kwargs.pop(key))

    def _build_(self, suggestion: tuple[Pixels, Pixels]) -> None:
        assert self._is_nested()
        assert self._native_ is None
        w, h = suggestion
        self._native_, native_dims = self._native_build_(suggestion)

    def _demolish_(self) -> None:
        assert self._is_built()
        assert self._native_ is not None

    def _place_(self, position: tuple[Pixels, Pixels]) -> None:
        assert self._is_built()
        return super()._place_(position)

    def _pickup_(self) -> None:
        assert self._is_placed()
        return super()._pickup_()

    @abstractmethod
    def _native_build_(
        self,
        suggestion: tuple[Pixels, Pixels],
        **buildattrs,
    ) -> tuple[NativeElement, tuple[Pixels, Pixels]]:
        raise NotImplementedError

    @abstractmethod
    def _native_style_(self, **styleattsr) -> None:
        raise NotImplementedError

    @classmethod
    def _subclass_sugar_(cls, subcls: Type[PlatformWidget]) -> None:
        if cls is subcls:
            return

        assert (
            subcls._native_build_ is not cls._native_build_
        ), f"{subcls} does not must define ._native_build_(...) classes, subclasses of {cls} do do"
        assert (
            subcls._native_style_ is not cls._native_style_
        ), f"{subcls} does not must define ._native_style_(...) classes, subclasses of {cls} do do"
