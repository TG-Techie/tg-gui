import gc
from tg_gui.prelude import *

if isoncircuitpython():
    gc.collect()
    print(gc.mem_free())


@main(screen := default.screen(), default.theme())
@application
class Test(Layout):

    _theme_ = SubTheme({Button: dict(size=2)})

    body = VStack(
        Button("hello", action=self.say("hello")),
        Button("goodbye", action=self.say("bye!")),
        Button("done", action=guiexit),
    )
    # body = VStack(
    #     VStack(
    #         Label("date:"),
    #         Date("{year}-{month}-{day}"),
    #     ),
    #     Date("{hour}:{sec}"),
    #     Button("hello", action=self.say("hello")),
    #     Button("goodbye", action=self.say("bye!")),
    #     Button("done", action=guiexit),
    # )

    def _layout_(self):
        self.body(center, self.dims)

    def say(self, msg: str) -> None:
        print(msg)


if isoncircuitpython():
    gc.collect()
    print(gc.mem_free())


if __name__ == "__main__":

    if isoncircuitpython():
        screen._register_recurring_update_(
            screen,
            lambda: print(gc.mem_free()),
            10.0,
        )

    screen.run()
