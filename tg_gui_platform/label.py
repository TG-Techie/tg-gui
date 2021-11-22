from tg_gui_core import State, Color, StyledWidget, themedwidget, align
from tg_gui_core.dimension_specifiers import DimensionSpecifier
from ._platform_impls._platform_ import label as _label_impl


@_label_impl.format_class
@themedwidget
class Label(StyledWidget):
    _offer_priority_ = 0
    _reserve_space_ = True
    _self_sizing_ = property(lambda self: isinstance(self._text, str))

    _use_sug_width_ = property(lambda self: isinstance(self._text, str))
    _use_sug_height_ = True

    _default_styling_ = dict(
        style=dict(color=0xFFFFFF),
        size=1,
        align=align.center,
    )

    _stateful_style_attrs_ = {"color": Color}
    _fixed_style_attrs_ = {
        "size": int,
        "align": align,  # type: ignore
    }

    _impl_build_ = _label_impl.build
    _impl_set_size_ = _label_impl.set_size
    _impl_apply_style_ = _label_impl.apply_style

    _set_text_ = _label_impl.set_text

    @property
    def text(self):
        return self._text.value(self) if isinstance(self._text, State) else self._text

    def __init__(self, text: str | State[str], **kwargs) -> None:
        super().__init__(**kwargs)
        assert isinstance(text, (str, State))
        self._text = text

    def _build_(self, dim_spec: DimensionSpecifier):

        text_src = self._text
        if isinstance(text_src, State):
            text_src._register_handler_(self, self._set_text_)

        super()._build_(dim_spec)

        self._set_text_(self.text)  # use property to get the raw string to show

    def _demolish_(self):
        if isinstance(self._text, State):
            self._text._deregister_handler_(self)
        super()._demoslish()
