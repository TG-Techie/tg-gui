from tg_gui.prelude import *


@main(
    screen := default.screen(),
    theme := default.theme(),
)
@application
class Test(Layout):

    _theme_ = SubTheme(
        {
            Button: dict(
                size=2,
                # style=Style(fill=color.red),
            )
        }
    )

    body = VStack(
        hello := Button("hello", action=self.say("hello")),
        goodbye := Button("goodbye", action=self.say("bye!")),
        done := Button("done", action=guiexit),
    )

    def _layout_(self):
        self.body(center, self.dims)

    def say(self, msg: str) -> None:
        print(msg)


if __name__ == "__main__":
    screen.run()
