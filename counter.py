from tg_gui import *


@widget
class Application(View):

    count = State(0)

    body = lambda self: VStack(
        Text(count >> "count: {}".format),
        Button("+", self.add_count(1)),
        Button("-", self.add_count(-1)),
        Button("done", action=close),
    )

    def add_count(self, amount: int) -> None:
        self.count += amount


app = main(Application)

if __name__ == "__main__":
    app.run()
