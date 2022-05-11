from __future__ import annotations

from tg_gui.prelude import *


@widget
class Application(View):

    message: str = StatefulAttr("hello")

    body: ViewSyntax[Application] = lambda self: Text(self.message)


if __name__ == "__main__":
    app = main(Application)
    app.run()
