from typing import Optional, Tuple, Callable, NoReturn
from . import _platform_

__all__ = (
    "_platform_",
    "guiexit",
)

SizeHint = Tuple[Optional[int], Optional[int]]
guiexit: Callable[[], NoReturn]
