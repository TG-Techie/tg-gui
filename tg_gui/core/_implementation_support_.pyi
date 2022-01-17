def class_id(cls: type) -> int:
    return id(cls)

def enum_compat(cls):
    return cls

def warn(msg: str) -> None:
    raise Warning(msg)

isoncircuitpython = lambda: False
