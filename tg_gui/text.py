from __future__ import annotations

from typing import TYPE_CHECKING, Generic, TypeVar

if TYPE_CHECKING:
    from typing import Callable, ClassVar
    from typing_extensions import Self

# ---

from ._lib_env import *
from .platform import text as _text


@widget
class Text(NativeWidget):

    text: str | Proxy[str] = StatefulAttr(init=True)

    build = _text.build
    update_style = _text.update_style

    onupdate_text = StatefulAttr.onupdate(text, _text.onupdate_text)


Text.build
Text.onupdate_text
