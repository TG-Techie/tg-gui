from __future__ import annotations

from tg_gui_core import annotation_only

# ---

from tg_gui_core import *

from .shared import NativeElement, NativeContainer
from .._platform_setup_ import *

# ---

if annotation_only():
    from fontio import BuiltinFont
    from adafruit_bitmap_font.bdf import BDF
    from adafruit_bitmap_font.pcf import PCF

from terminalio import FONT as _FONT
from adafruit_display_text import LabelBase, wrap_text_to_pixels, wrap_text_to_lines
from adafruit_display_text.label import Label as TextLabel
from adafruit_display_text.bitmap_label import Label as BitmapLabel


@widget
class Text(NativeWidget[LabelBase]):

    text: str = StatefulAttr(init=True, kw_only=False)

    # --- themed attrs ---
    # these should be themed/environment vars
    foreground: Color = StatefulAttr(default=Color.white)
    font: BuiltinFont | BDF | PCF = _FONT

    @onupdate(text)
    def onupdate_text(self, text: str) -> None:
        self.native.text = text

    def onupdate_theme(self, attr: ThemedAttr[Any] | None) -> None:
        print(f"WARNING: Text.onupdate_theme() not implemented")
        self.native.color = self.foreground

    def _build_(
        self,
        suggestion: tuple[Pixels, Pixels],
        *,
        text: str | State[str],
    ) -> tuple[LabelBase, tuple[Pixels, Pixels]]:
        variable_width = isinstance(text, State)

        label: LabelBase
        if variable_width:
            label = TextLabel(
                self.font,
                # max_glyphs=len(self.text),
                text=text,
            )
        else:
            label = BitmapLabel(
                self.font,
                text=text,
            )

        return label, label.bounding_box[2:4]

    def _demolish_(self, native: LabelBase) -> None:
        del native

    def _place_(
        self,
        container: NativeContainer,
        native: LabelBase,
        pos: tuple[Pixels, Pixels],
        abs_pos: tuple[Pixels, Pixels],
    ) -> None:
        container.append(native)
        native.x = pos[0]
        native.y = pos[1]

    def _pickup_(self, container: NativeContainer, native: LabelBase) -> None:
        container.remove(native)
