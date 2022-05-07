from __future__ import annotations

from tg_gui.prelude import *


@widget
class App(View):

    body: ViewSyntax[App] = lambda self: (
        Button(
            "test",
            action=lambda: print("Hello, world!"),
        )
    )
