class _BracketBypass:
    def __init__(self, *, ret=None, passthru=False):
        self._ret = ret
        self._passthru = passthru

    def __getitem__(self, value, *_):
        return value if self._passthru else self._ret


_bracket_returns_objecct = _BracketBypass(ret=object)
Callable = _bracket_returns_objecct
Union = _bracket_returns_objecct
Generic = _bracket_returns_objecct

_type_passthorugh = _BracketBypass(passthru=True)
Type = _type_passthorugh
ClassVar = _type_passthorugh

TypeVar = lambda _: None

Protocol = object  # type: ignore
Any = object
