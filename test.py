from __future__ import annotations


import tg_gui


def prettydict(d: dict[Any, Any]) -> str:
    return (
        "{\n    "
        + ",\n    ".join(
            f"{k!r}: \t{prettydict(v) if isinstance(v, dict) else repr(v)}"
            for k, v in sorted(d.items())
            if not k.startswith("_")
        )
        + "\n}"
    )


print(prettydict(tg_gui.__dict__))

from tg_gui import *


from typing import *


def VStack(w):
    return w


SomeWidget = TypeVar("SomeWidget", bound=Widget)

from tg_gui import *

from tg_gui.view import ViewBody


@widget
class Application(View):

    body: ViewBody[Application] = lambda self: Button(
        "hello",
        action=self.say("hello"),
    )

    def say(self, text: str) -> None:
        print(text)


print(Application)

if __name__ == "__main__":
    app = main(Application, size=(100, 90))
    app.run()
