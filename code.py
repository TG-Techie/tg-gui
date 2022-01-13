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
class Test(Layout):

    _theme_ = Theme(
        {
            Label: {Label.size: 2},
            Date: {Date.foreground: color.white},
        }
    )

    tgl_state = State(False)
    tgl_color = DerivedState(tgl_state, lambda s: color.red if s else color.green)

    body = lambda: VStack(
        Label("indicator", foreground=self.tgl_color),
        Button("Toggle", action=self.toggle),
    )

    # body = widgetbuilder(
    #     lambda: VStack(
    #         Date("{hour}:{min}", size=6),
    #         Date("{dayshort} {monthday} {monthshort}", size=3),
    #         Date("{sec}"),
    #     )
    # )

    def say(self, msg: str):
        print(msg)

    def toggle(self) -> None:
        before = self.tgl_color
        self.tgl_state = not self.tgl_state
        st: DerivedState[Color] = type(self).tgl_color
        print("toggle", self, before, self.tgl_color, st._registered)

    # @layoutmethod
    def _layout_(self):
        self.body(center, self.dims)


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
