from tg_gui_core import annotation_only

if annotation_only():
    from displayio import Shape, Group, TileGrid, Palette, Bitmap, OnDiskBitmap

    NativeElement = Group | Shape | TileGrid | Palette | Bitmap | OnDiskBitmap
    NativeContainer = Group
else:
    NativeElement = object
    NativeContainer = object
