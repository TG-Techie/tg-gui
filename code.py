from tg_gui.prelude import *


@main(screen := default.screen(), default.theme())
@application
class Test(Layout):

    _theme_ = SubTheme(
        {
            Button: dict(size=2),
        }
    )

    VStack
    # body = VStack(
    #     VStack(
    #         Label(
    #             Date.secs >> f"example {i}: {{}}".format,
    #             size=2,
    #         )
    #         for i in range(3)
    #     ),
    #     Button("hello", action=self.say("hello")),
    #     Button("goodbye", action=self.say("bye!")),
    #     Button("done", action=guiexit),
    # )

    entries: ListState[tuple[int, str]] = ListState([(0, "example")])

    if False:
        body = VList(Label(f"{idnum}: {msg}") for idnum, msg in entries)

    body = VStack(
        Button("+", action=self.add_entry),
        VList(
            entries,
            lambda pack: Label("{}: {}".format(*pack)),
        ),
    )

    def _layout_(self):
        self.body(center, self.dims)

    # def say(self, msg: str) -> None:
    #     print(msg)

    def add_entry(self):
        nextid = 1 + max(idnum for idnum, _ in self.entries)
        msg = input("msg: ")
        self.entries.append((nextid, msg))


if __name__ == "__main__":
    screen.run()
