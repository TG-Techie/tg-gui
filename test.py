from __future__ import annotations


import tg_gui


print(
    "{",
    "    "
    + ",\n    ".join(
        f"{k!r}: \t{v!r}"
        for k, v in sorted(tg_gui.__dict__.items())
        if not k.startswith("_")
    ),
    "}",
    sep="\n",
)

from tg_gui import *


from typing import *


def VStack(w):
    return w


# @main
@widget
class Application(View):

    body = lambda self: Button(
        "hello",
        action=self.say("hello"),
    )

    def say(self, text: str) -> None:
        print(text)


Application.body

app = Application()
