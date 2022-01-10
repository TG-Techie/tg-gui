import digitalio
import pwmio
import displayio
import board

import time

from adafruit_focaltouch import Adafruit_FocalTouch

displayio.release_displays()

WARP_Y = 15

# --- ports ---

spi = board.SPI()
i2c = board.I2C()


# --- display ---


_backlight = pwmio.PWMOut(board.BACKLIGHT, frequency=200, duty_cycle=0)

LOWER_OFFSET = 0.2


def backlight(value: None | float = None):
    if value is None:
        return _backlight.duty_cycle
    _backlight.duty_cycle = int(
        65535 * ((1 - LOWER_OFFSET) * value + LOWER_OFFSET),
    )


display = displayio.Display(
    _display_bus := displayio.FourWire(
        spi,
        command=board.TFT_DC,
        chip_select=board.TFT_CS,
        reset=board.TFT_RST,
        baudrate=1000_000_000,
    ),
    # source: https://github.com/adafruit/Adafruit_CircuitPython_ST7789
    (
        b"\x01\x80\x96"  # _SWRESET and Delay 150ms
        b"\x11\x80\xFF"  # _SLPOUT and Delay 500ms
        b"\x3A\x81\x55\x0A"  # _COLMOD and Delay 10ms
        b"\x36\x01\x08"  # _MADCTL
        b"\x21\x80\x0A"  # _INVON Hack and Delay 10ms
        b"\x13\x80\x0A"  # _NORON and Delay 10ms
        b"\x36\x01\xC0"  # _MADCTL
        b"\x29\x80\xFF"  # _DISPON and Delay 500ms
    ),
    width=240,
    height=240,
    rotation=180,
    rowstart=80,
    auto_refresh=False,
)

display.show(displayio.Group())
display.refresh()


backlight(0.5)

# --- touch ---

_touchscreen = Adafruit_FocalTouch(
    i2c,
    # commented b/c lib waits forever # irq_pin=digitalio.DigitalInOut(board.CTP_INT),
)
_touchscreen_reset = digitalio.DigitalInOut(board.CTP_RST)
_touchscreen_reset.switch_to_output()


def _reset_touchscreen(_pin=_touchscreen_reset):
    # global touchscreen_reset
    print("resetting touchscreen")
    _pin.value = True
    time.sleep(0.005)

    _pin.value = False
    time.sleep(0.005)

    _pin.value = True
    time.sleep(0.3)


_reset_touchscreen()

# --- standardized driver functions ---


def poll_single_touchpoint() -> tuple[int, int] | None:
    """
    Polls the touch screen for a single touch point.
    Returns a tuple of the x and y coordinates of the touch point.
    If no touch point is detected, returns None.
    """

    if not _touchscreen.touched:
        return None
    else:
        point_dict = _touchscreen.touches[0]
        return (
            int(240 * point_dict["x"] / 300),
            max(0, int(240 * point_dict["y"] / 300) - WARP_Y),
        )
