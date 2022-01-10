# TG-Gui's Bindings to Native Elements

### `_platform_impls/`

This package contains the functions, methods, and classes that the `tg_gui`'s standard library is built ontop of. Thess implementations ("impls") take a platform's graphics/ui pimitives and expose them as a uniform interface for TG-Gui to run on-top of

### Layout and Interface

Platform implementations structure themselves as modules that contain functions, methods, and hooks `tg_gui_platform` uses (depends on) to manage as parts of the TG-Gui standard library.

The `_platform_/` folder contains a stubbed version of what all implementations need to implement. While is is underdevelopment, when the stub is confusing or needs additional epxlanations please feel free to make an issue asking about it or a pull to add explination.

### TODO: provide more details and theory...

why as methods vs classes, when should things be or not be used. etc..
for now, in short:
they are separated to that the business and framework level logic.

### Terminology

- `native element` - The datascructures, objects, and/or functions taht implement core graphical behavior. For platforms like `Qt` (or potentially `UIKit/AppKit`) this exposes Buttons, Labels, Application windows, etc. For platforms like circuitpython this composes rectangles, text, etc into buttons, labels, etc and serves the same place as a high level framework like `UIKit` or `Qt`.
- `# TODO:` - elaborate on Widget,
- `platform`
- `impl`
- `etc...`
