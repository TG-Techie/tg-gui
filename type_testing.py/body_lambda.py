class HStack:
    pass


class View:

    build = lambda self: HStack()


v = View()
b = v.build()
