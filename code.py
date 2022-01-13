import gc
import sys

if sys.implementation.name in {"circuitpython", "micropython"}:
    import drivers

from tg_gui.prelude import *

if (
    __debug__ and "--step-print-debug" in sys.argv
):  # change `True` based on your preference
    from tg_gui_core import use_step_print_debugging

    use_step_print_debugging(True)

if isoncircuitpython():
    gc.collect()
    print(gc.mem_free())


@main(screen := default.screen())
@application
class Test(View):

    _theme_ = SubTheme(
        {
            Label: {Label.size: 2},
            Date: {Date.foreground: color.white},
        }
    )

    body = lambda: VStack(
        Date("{hour}:{min}", size=6),
        Date("{dayshort} {monthday} {monthshort}", size=3),
        Date("{sec}"),
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
