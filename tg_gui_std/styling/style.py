from tg_gui_core import Widget, State, DerivedState, uid


_errfmt = lambda items: "{" + (", ".join(str(item) for item in items)) + "}"


class Style:

    # def __new__(): dispatch to Style or StatefulStyle

    def __init__(self, **attrs):
        self._id_ = uid()
        self._styled_attrs = attrs
        self._confd_type = None
        self._confd_theme_id = None
        self._confd_style_entry = None

    def __iter__(self):
        return self.keys()

    def keys(self):
        assert self._isconfigured()
        return iter(self._confd_style_entry)

    def __getitem__(self, key):
        assert self._isconfigured(), self
        return self._styled_attrs.get(key, self._confd_style_entry[key])

    def items(self):
        attrs = self._styled_attrs
        for key, default in self._confd_style_entry.items():
            yield (key, attrs.get(key, default))

    def __contains__(self, key):
        assert self._isconfigured()
        return key in self._confd_style_entry

    def _isconfigured(self):
        return self._confd_type is not None

    def _configure_(self, *args):

        # input parsing
        if len(args) == 1:
            (inst,) = args
            assert isinstance(inst, Widget)
            cls = type(inst)
            theme = inst._superior_._theme_
        elif len(args) == 2:
            cls, theme = args
            assert isinstance(cls, type) and issubclass(cls, Widget)
            # cannot be used with new structure # assert isinstance(theme, Theme)
        else:
            raise TypeError(
                f"{type(self)}._configure_(...) expected one or two arguemtns, got {len(args)}"
            )

        # config dispatch
        if self._isconfigured():
            self._cls_matches_config(cls, theme)
        else:
            self._configure(cls, theme)

    def _cls_matches_config(self, cls, theme):
        assert issubclass(cls, self._confd_type), (
            f"{self} cannot be configured for a {cls}, "
            + f"already configured for widgets of type {self._confd_type}"
        )
        assert theme._id_ == self._confd_theme_id, (
            f"{self} already configured to theme with id {self._confd_theme_id}.\n"
            + f"tried to configure to {theme}"
        )

    def _configure(self, cls, theme):

        # cannot be used with new strucutre # assert issubclass(cls, StyledWidget), (
        #     f"{self} cannot be used to configure {cls}."
        #     f" Expected an instance of StyledWidget, found an object of type {cls.__qualname__}"
        # )

        self._confd_type = confd_type = cls
        self._confd_theme_id = theme._id_
        self._confd_style_entry = theme._get_base_styling_for_(confd_type)["style"]

        assert self._config_okay()

    def _config_okay(self):
        default_attrs = self._confd_style_entry
        required_attrs = self._confd_type._stateful_style_attrs_

        assert all((attr in default_attrs) for attr in self._styled_attrs), (
            f"{self} got unexpected attr(s) {_errfmt(set(self._styled_attrs) - set(default_attrs))}.\n"
            + f"missing {_errfmt(set(default_attrs) - set(self._styled_attrs))}"
        )
        assert all(
            (attr in required_attrs) for attr in self._styled_attrs
        ), f"unexpected attr(s) {_errfmt(set(self._styled_attrs) - set(required_attrs))}"

        return True


class DerivedStyle(DerivedState, Style):
    def __init__(self, states, **attrs):

        # input formatting
        if isinstance(states, State):
            states = (states,)
        elif isinstance(states, tuple):
            pass
        else:
            raise ValueError(f"argument states must be a State or tuple of States")

        super(DerivedState, self).__init__(value=self)

        self._src_states = states
        self._derived_style = {}

        self._styled_attrs = attrs
        self._confd_type = None
        self._confd_theme_id = None
        self._confd_style_entry = None
        self._substates = None

        self._register_with_sources()

    def _configure(self, cls, theme):
        """
        TODO: add expl.
        """

        super()._configure(cls, theme)

        self._update_from_sources(self)

    def __getitem__(self, key):
        assert self._isconfigured()
        return self._derived_style.get(key, self._confd_style_entry[key])

    def _update_from_sources(self, _):
        """
        a hander that recalcuates the derived state from the given source states
        and updates any handlers registered to this state
        """
        assert self._isconfigured()
        self._derive_style()
        self._alert_registered(self)

    def _derive_style(self):
        substates = [state.value(self) for state in self._src_states]

        self._derived_style = foo = {
            attr: self._calc_style_attr(attr, substates)
            for attr, default in self._styled_attrs.items()
        }

    def _calc_style_attr(self, attr, substates):
        spec = self._styled_attrs.get(attr, self._confd_style_entry[attr])
        return spec(*substates) if callable(spec) else spec
