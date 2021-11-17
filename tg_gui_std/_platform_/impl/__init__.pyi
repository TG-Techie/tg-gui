from typing import *

# TODO: add Window to the stg libaray idiom

from . import button
from . import label
from .screen import Screen

# module for setting up environments
from . import prelude

Native = Any

__all__ = (
    "button",
    "label",
    "Screen",
    "Native",
)
