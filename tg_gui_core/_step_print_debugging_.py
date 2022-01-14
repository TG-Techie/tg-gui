from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Callable, NoReturn


import builtins
from builtins import print as _orig_print


def use_step_print_debugging(use_on: bool):
    if not use_on:
        builtins.print = _orig_print
    else:
        builtins.print = _step_print


def _raise(exception):
    raise exception  # !! step print internals


_step_cmds: dict[tuple[str, ...], tuple[Callable[[], None | NoReturn], str]] = {
    ("raise",): (
        lambda: _raise(Exception("step print debug raise")),  # !! step print internals
        "raise an exception",
    ),
    ("", "continue", "c"): (
        None,
        "exit the step session and conintue executing python as normal",
    ),
    ("help",): (
        lambda: _orig_print(
            "commands include:\n    "
            + "\n    ".join(
                f"{', '.join(map(repr, cmd))}: \t{desc}"
                for cmd, (_, desc) in _step_cmds.items()
            )
        ),
        "this help message",
    ),
}


def _step_print(*args, end: str = "\n", **kwargs):
    _orig_print(*args, **kwargs, end="")

    prompt_header = end.rstrip() + " "

    while True:
        cmd = input(prompt_header + "# (step cmd): ").strip()
        prompt_header = ""

        for cmds, (fn, _) in _step_cmds.items():
            if cmd in cmds:
                if fn is not None:
                    fn()  # !! step print internals
                else:
                    return
        else:
            print(f"Unkown command: `{cmd}`")
