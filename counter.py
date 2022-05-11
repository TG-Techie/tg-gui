from __future__ import annotations
import abc

abc.ABC = object

from tg_gui.prelude import *


@widget
class Application(View):

    message = State("hello")

    body: ViewSyntax[Application] = lambda self: Text(self.message)


if __name__ == "__main__":
    app = main(Application)
    app.run()
else:
    app = Application()
