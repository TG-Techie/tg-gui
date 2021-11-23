from typing import *
from typing import TextIO

LineTransform = Callable[[int, str], str]


def foreach_line(
    fromfile: TextIO,
    intofile: TextIO,
    transform: LineTransform | Iterable[LineTransform],
    tab_replacement=" " * 4,
) -> None:

    try:
        transforms = tuple(transform)
    except:
        transforms = (transform,)

    assert fromfile.readable(), f"passed file '{fromfile.name}' not readable"
    assert intofile.writable(), f"passed file '{intofile.name}' not writable"

    last_indent = ""
    indentation = 0
    for linesrc in fromfile:
        linesrc = linesrc.rstrip("\n\r")

        src = linesrc.lstrip()
        indent = linesrc[0 : -len(src)]

        assert indent + src == linesrc, (
            "indentations and body incorrectly separated "
            f"{indent!r}+{src!r} != {linesrc!r}"
        )

        indent = indent.replace("\t", tab_replacement)

        if len(indent) > len(last_indent):
            indentation += 1
        elif len(indent) < len(last_indent):
            indentation -= 1
        assert indentation >= 0, indentation
        last_indent = indent

        # separate into body and indentations
        outtxt = src
        for fn in transforms:
            outtxt = transform(indentation, outtxt)

        intofile.write(indent + (outtxt) + "\n")


def remove_type_import(
    indentation: int,
    body: str,
) -> str:

    tokens = body.replace(".", " ").split()

    writeout = body
    if len(tokens) >= 2 and tokens[0] in {"from", "import"} and tokens[1] == "typing":
        writeout = "pass  # removed # " + writeout
    else:
        replacement = '(False and "type checking optimization")'
        writeout = writeout.replace("typing.TYPE_CHECKING", replacement)
        writeout = writeout.replace("TYPE_CHECKING", replacement)

    return writeout


def constify_isoncircuitpython(indentation: int, body: str) -> str:
    writeout = body
    const_fn_call = "isoncircuitpython()"
    if const_fn_call in writeout and "def" not in writeout:
        writeout = writeout.replace(
            const_fn_call,
            '(False and "removed for bytecode optimization")',
        )
    return writeout


if __name__ == "__main__":
    pass  # TODO: add command line interface here
