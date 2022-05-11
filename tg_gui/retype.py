from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import TypeVar, Generic, ClassVar, Callable, Any, Type
    from typing_extensions import dataclass_transform

    from .state import StatefulAttr
    from tg_gui_core.attrs import WidgetAttr

    _T = TypeVar("_T")

    @dataclass_transform(
        eq_default=False,
        order_default=False,
        kw_only_default=True,
        field_descriptors=(
            WidgetAttr,
            StatefulAttr,
        ),
    )
    def widget(cls: Type[_T]) -> Type[_T]:
        ...

else:
    from tg_gui_core.attrs import widget
