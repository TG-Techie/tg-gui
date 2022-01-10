import gc


from tg_gui.prelude import *

if isoncircuitpython():
    gc.collect()
    print(gc.mem_free())


m = main(
    screen := default.screen(),
    default.theme(),
    _startup=__name__ == "__main__",
)


@m
@application
class Test(Layout):

    _theme_ = SubTheme(
        {
            Button: dict(size=3),
            Label: dict(size=3),
        }
    )

    body = VStack(
        Date.dateshort(),
        Date.time(secs=True),
        Button("hello", action=self.say("hi")),
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
            5.0,
        )

    screen.run()
