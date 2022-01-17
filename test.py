import tg_gui


print(
    "{",
    "    "
    + ",\n    ".join(
        f"{k!r}: \t{v!r}"
        for k, v in sorted(tg_gui.__dict__.items())
        if not k.startswith("_")
    ),
    "}",
    sep="\n",
)
