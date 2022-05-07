from tg_gui.prelude import *


@widget
class Application(View):

    # count = State(0)

    body = lambda self: Widget()


app = main(Application)

if __name__ == "__main__":
    app.run()
