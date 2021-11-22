from tg_gui.prelude import *


@main(screen := default.screen(), default.theme())
@application
class Test(Layout):

    _theme_ = SubTheme(
        {
            Button: dict(size=2),
        }
    )

    body = VStack(
        Date.time(size=2, align=align.center),
        Button("hello", action=self.say("hello")),
        Button("goodbye", action=self.say("bye!")),
        Button("done", action=guiexit),
    )

    def _layout_(self):
        self.body(center, self.dims)

    def say(self, msg: str) -> None:
        print(msg)


if __name__ == "__main__":
    screen.run()
