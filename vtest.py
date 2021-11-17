from tg_gui_std import isoncircuitpython
from tg_gui_std.prelude import *

if isoncircuitpython():
    from drivers import display
else:
    display = None


@main(screen(display=display), theme())
@application
class Test(Layout):

    body = VStack(
        Button("hello", action=lambda: print("hello"), size=2),
        Button("goodbye", action=lambda: print("bye!"), size=2),
    )

    def _layout_(self):
        self.body(center, self.dims)


# @main
# @application
# class Test(Layout):

#     body = VStack(
#         Label("foo"),
#         Button("hello", action=lambda: print("hello")),
#         Button("world", action=lambda: print("world")),
#     )
#     quit = Button("Quit", action=sys.exit)

#     def _layout_(self):
#         self.body(top, self.dims)
#         self.quit((right, top), (self.width // 4, self.height // 6))


if __name__ == "__main__":
    screen.run()
