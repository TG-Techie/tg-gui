import gc
from tg_gui.prelude import *

if isoncircuitpython():
    gc.collect()
    print(gc.mem_free())


@main(
    screen := default.screen(),
    default.theme(),
)
@application
class Test(View):

    _theme_ = SubTheme(
        {
            Label: {
                Label.foreground: color.red,
                Label.size: 2,
            },
            Date: {
                Date.foreground: color.white,
            },
        },
    )

    body = lambda: VStack(
        Date("{hour}:{min}", size=6),
        Date("{dayshort} {monthday} {monthshort}", size=3),
        Date("{sec}"),
        Label("test"),
    )

    def say(self, msg: str) -> None:
        print(msg)


if isoncircuitpython():
    gc.collect()
    print(gc.mem_free())


if __name__ == "__main__":

    # if isoncircuitpython():
    #     screen._register_recurring_update_(
    #         screen,
    #         lambda: print(gc.mem_free()),
    #         10.0,
    #     )

    screen.run()
