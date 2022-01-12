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
class Test(Layout):

    _theme_ = SubTheme(
        {
            Button: dict(size=2),
            Label: dict(size=2),
        }
    )

    body = VStack(
        HStack(
            Date("{hour}"),
            Label(":"),
            Date("{min}"),
            theme={Label: dict(size=6, fit_to=True)},
        ),
        HStack(
            Date("{dayshort}"),
            Date("{monthday}"),
            Date("{monthshort}"),
            theme={Label: dict(size=3, fit_to=True)},
        ),
        align=align.leading,
    )

    def _layout_(self):
        self.body(center, self.dims)

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
