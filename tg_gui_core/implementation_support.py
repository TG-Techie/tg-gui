from sys import implementation as _implementation


if _implementation.name == "cpython":
    from ._impl_support_cpython import *
elif _implementation.name == "circuitpython":
    from ._impl_support_circuitpy import *
else:
    raise NotImplementedError(
        "tg_gui (and tg_gui core) does not currently support the "
        + f"{repr(_implementation.name)} python implementation"
    )

locals()["TYPE_CHECKING"] = False
