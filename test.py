from __future__ import annotations

from tg_gui import *
import sys


@widget
class Application(View):

    count = State(0)

    body = lambda self: VStack(
        HStack(
            Button("+", action=self.inc(1)),
            Button("-", action=self.inc(-1)),
        ),
        Button("hello", action=self.say(self.count)),
        Button("quit", action=sys.exit),
    )

    def say(self, text) -> None:
        print(text)

    def inc(self, by: int) -> None:
        self.count += by


if __name__ == "__main__":
    window = main(Application, fit=True)  # , size=(50, 50))
    window.run()
