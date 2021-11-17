import time
import gc


class Foo:
    def __init__(self, count) -> None:
        self.x = 0
        self._count = count

    def methda(self):
        for _ in range(self._count):
            if self.x >= 0:
                self.x = self.x + 1

    def methdb(self):
        for _ in range(self._count):
            if (x := self.x) >= 0:
                self.x = x + 1


while True:
    count = int(input("how many: ").strip())

    f = Foo(count)
    start = time.monotonic()
    gc.collect()
    f.methda()
    print(a := time.monotonic() - start)

    f = Foo(count)
    start = time.monotonic()
    gc.collect()
    f.methdb()
    print(b := time.monotonic() - start)

    print("method a" if a > b else "method b", a / b)
