from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from displayio import Shape, Group, TileGrid, Palette, Bitmap, OnDiskBitmap

    NativeElement = Group | Shape | TileGrid | Palette | Bitmap | OnDiskBitmap
    NativeContainer = Group
else:
    NativeElement = object
    NativeContainer = object
