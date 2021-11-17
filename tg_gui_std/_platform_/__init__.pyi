from typing import Optional, Tuple, Callable, NoReturn
from . import impl

prelude = impl.prelude
SizeHint = Tuple[Optional[int], Optional[int]]
guiexit: Callable[[], NoReturn]
