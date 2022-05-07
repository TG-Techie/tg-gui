from __future__ import annotations
from typing import *

from tg_gui_core.attrs import *


@widget
class Widget:
    __is_widget_class__: ClassVar[Literal[True]] = True  # impl detail

    id = WidgetAttr(init=False, default_factory=UID)
    superior = WidgetAttr(init=False)
    ...


@widget
class Button(Widget):
    title: str = WidgetAttr(init=True, kw_only=False)
    action: Callable[[], None] = WidgetAttr(init=True)
    ...


w = Widget()
b = Button("test", action=lambda: print("test"))

print(w.__dict__)  # {'_id': 6, '_superior': Missing}
print(
    b.__dict__
)  # {'_title': 'test', '_id': 7, '_superior': Missing, '_ac...tion': <function <lambda> at 0x1040df250>}
