from adafruit_stmpe610 import Adafruit_STMPE610_SPI
import adafruit_ili9341
import digitalio
import displayio
import board
import neopixel
import time
from time import monotonic_ns
import atexit


# import msgpack
import json

# --- import congif and unpack data ---
with open("driver_config.json", "br") as file:
    config = json.load(file)
del file

# T = Top, B = Bottom, L = Left, R = Right
assert config["touch"]["kind"] == "resistive"
_LX, _TY, _RX, _BY = config["touch"]["coords"]

assert config["display"]["driver"] == "ILI9341"
_ROTATION = config["display"]["rotation"]
_WIDTH, _HEIGHT = config["display"]["size"]

del config

# --- ports ---

spi = board.SPI()

tft_cs = board.IO1
tft_dc = board.IO3
touch_cs = board.IO38
neo_pin = board.IO7

# --- driver objects ---

# turn the pixel on as a reminder if the trace is not cut
pixel = neopixel.NeoPixel(neo_pin, 1, auto_write=True)
pixel[0] = 0xEF0000

# setup the display
displayio.release_displays()
display_bus = displayio.FourWire(spi, command=tft_dc, chip_select=tft_cs)
display = adafruit_ili9341.ILI9341(
    display_bus,
    width=_WIDTH,
    height=_HEIGHT,
    rotation=_ROTATION,
)


# resistive touchscreen
touch = Adafruit_STMPE610_SPI(
    spi,
    digitalio.DigitalInOut(touch_cs),
)


# --- driver interface ---

_XRANGE = abs(_LX - _RX)
_YRAGNE = abs(_TY - _BY)
print((_LX > _RX, _XRANGE), (_TY > _BY, _YRAGNE))
_FLIPX = -1 if _LX > _RX else 1
_FLIPY = -1 if _TY > _BY else 1


_prev_coord: tuple[int, int] | None = None


def poll_single_touchpoint() -> tuple[int, int] | None:
    global _prev_coord

    prev = _prev_coord

    if not touch.touched:
        # if data is not None and prev is None:

        if touch.buffer_size:
            # clear the buffer
            for _ in range(touch.buffer_size + 1):
                touch.read_data()

        _prev_coord = None
        return None

    else:
        if prev is None:
            touch.read_data()
            touch.read_data()
            touch.read_data()
            touch.read_data()
            touch.read_data()

        y, x, strength = touch.read_data()  # touch.read_data()

        coord = _prev_coord = (
            int(_WIDTH * _FLIPX * (x - _LX) / _XRANGE),
            int(_HEIGHT * _FLIPY * (y - _TY) / _YRAGNE),
        )

        return coord


# def stream_raw_touch_data():
#     while True:
#         if touch.buffer_empty:
#             pass
#         else:
#             print(time.monotonic(), touch.read_data())
#             time.sleep(0.01)


# def stream_scaled_touch_data():
#     while True:
#         if (p := get_touchpoint()) is not None:
#             print(p)
#             time.sleep(0.01)
