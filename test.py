from __future__ import annotations

from tg_gui import *
import sys


@widget
class Application(View):

    body: BodySyntax[Application] = lambda self: VStack(
        Button("hello", action=self.say("hello")),
        Button("quit", action=sys.exit),
    )

    def say(self, text: str) -> None:
        print(text)


if __name__ == "__main__":
    window = main(Application, size=(240, 240))
    window.run()
