import gc
import sys
import time

# import micropython

# micropython.opt_level(3)

if sys.implementation.name in {"circuitpython", "micropython"}:
    import drivers

from tg_gui.prelude import *

# from tg_gui_core._step_print_debugging_ import use_step_print_debugging

# use_step_print_debugging(True)

if isoncircuitpython():
    gc.collect()
    print("pre cls decl", gc.mem_free())


@main(screen := default.screen())
@application
@layoutwidget
class Test(View):

    _theme_ = Theme(
        {
            Label: {Label.size: 2},
            Date: {Date.foreground: color.white},
        }
    )

    tgl_state = State(False)
    tgl_color = DerivedState(tgl_state, lambda s: color.green if s else color.red)

    body = lambda: VStack(
        Date("{hour}:{min}", size=6),
        Date("{dayshort} {monthday} {monthshort}", size=3),
        HStack(
            Label(self.tgl_state >> str, foreground=self.tgl_color, fit_to=True),
            Button("<-Toggle", action=self.toggle(), size=2, fit_to_text=True),
        ),
    )

    def toggle(self, msg="") -> None:
        if msg:
            print(time.monotonic(), msg)
        self.tgl_state = not self.tgl_state


if isoncircuitpython():
    gc.collect()
    print("post cls decl", gc.mem_free())


if __name__ == "__main__":

    if isoncircuitpython():
        screen._register_recurring_update_(
            screen,
            lambda: print(time.monotonic(), gc.mem_free()),
            10.0,
        )

    screen.run()
