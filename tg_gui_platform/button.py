from tg_gui_core import Specifier, Color, isoncircuitpython
from .styling import StyledWidget, themedwidget
from ._platform_.impl import button as _button_impl

if not isoncircuitpython():
    from typing import Union, Callable
else:
    from tg_gui_core.typing_bypass import Union  # type: ignore


@_button_impl.format_class
@themedwidget
class Button(StyledWidget):
    _offer_priority_ = 0
    _reserve_space_ = True
    _self_sizing_ = True

    # user facing style
    _stateful_style_attrs_ = {
        "fill": Color,
        "text": Color,
        "active_fill": Color,
        "active_text": Color,
    }
    _fixed_style_attrs_ = {
        "radius": int,
        "size": Union[float, int],  # type: ignore
        "fit_to_text": bool,
    }

    # impl tie-in
    _impl_build_ = _button_impl.build
    _impl_set_size_ = _button_impl.set_size
    _impl_apply_style_ = _button_impl.apply_style

    _use_sug_width_ = property(
        lambda self: self._theme_.get_styling_for(Button)["fit_to_text"]
    )
    _use_sug_height_ = True

    text = property(lambda self: self._text)

    def __init__(
        self,
        text,
        *,
        action: Callable[[], None],
        **kwargs,
    ):
        super().__init__(**kwargs)
        self._text = text
        self._action_src = action
        self._action_ = None

    def _on_nest_(self):
        super()._on_nest_()

        action = self._action_src
        if isinstance(action, Specifier):
            action = action._resolve_specified_(self)
        self._action_ = action
