from __future__ import annotations

from tg_gui.all import *


@widget
class Application(View):

    message = State("hello")

    body: View.Syntax[Self] = lambda self: Text(self.message)


if __name__ == "__main__":
    app = main(Application)
    app.run()
else:
    app = Application()
