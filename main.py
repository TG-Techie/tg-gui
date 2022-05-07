from __future__ import annotations

from tg_gui.prelude import *


@widget
class App(View):

    body = lambda self: (
        Button(
            "test",
            action=self.say(("Hello, world!", self)),
        )
    )

    def say(self, message: str, view: View) -> None:
        print(message, view)


if __name__ == "__main__":
    main(App).run()
