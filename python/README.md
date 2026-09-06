# nitroglyph

Python bindings for controlling Acer Nitro keyboard RGB lighting through the NitroGlyph Linux driver.

`nitroglyph` provides a simple Python API for controlling keyboard zones, colors, brightness, and built-in lighting effects.

## Features

* Control individual RGB zones
* Control all zones at once
* Adjustable brightness (0-100%)
* Acer Built-in lighting effects:

  * Breath
  * Wave
  * Neon
  * Zoom
  * Shifting
* Optional effect duration handling

---

## Requirements

* Linux
* NitroGlyph kernel driver installed and loaded
* `/dev/nitro-glyph` device available

---

## Installation

```bash
pip install nitroglyph
```

For development:

```bash
git clone https://github.com/adhilsalim/nitro-glyph.git
cd python
pip install -e .
```

---

## Quick Start

```python
from nitroglyph import NitroGlyphController

ngc = NitroGlyphController()

ngc.enable()

ngc.set_zone(
    zone=1,
    red=255,
    green=0,
    blue=0
)

ngc.close()
```

---

## Zones

The Nitro keyboard is divided into four RGB zones.

| Zone | Description       |
| ---- | ----------------- |
| 1    | Left zone         |
| 2    | Center-left zone  |
| 3    | Center-right zone |
| 4    | Right zone        |
| 0    | All zones         |

Example:

```python
ngc.set_zone(
    zone=0,
    red=255,
    green=172,
    blue=28
)
```

---

## Brightness

Brightness is specified as a percentage between `0` and `100`.

```python
ngc.set_zone(
    zone=1,
    red=255,
    green=0,
    blue=0,
    brightness=50
)
```

The RGB values are automatically scaled according to the brightness level.

---

## Public API

### NitroGlyphController

Create a controller instance:

```python
from nitroglyph import NitroGlyphController

ngc = NitroGlyphController()
```

---
<!-- 
### enable()

Enables keyboard lighting control.

```python
ngc.enable()
```

---

### disable()

Turns off all keyboard lighting.

```python
ngc.disable()
``` -->

---

### clear()

Clears all keyboard zones and sets brightness to zero.

```python
ngc.clear()
```

---

<!-- ### close()

Closes the underlying device handle.

```python
ngc.close()
``` -->

---

### set_zone()

Set the RGB color of a specific zone.

```python
ngc.set_zone(
    zone=1,
    red=255,
    green=0,
    blue=0,
    brightness=100
)
```

Parameters:

* `zone` — Zone number (`0-4`)
* `red` — Red value (`0-255`)
* `green` — Green value (`0-255`)
* `blue` — Blue value (`0-255`)
* `brightness` — Brightness percentage (`0-100`)

---

## Effects

Effects can be used directly through `effect()` or through convenience methods.

### Mode Enum

```python
from nitroglyph import Mode
```

Available modes:

```python
Mode.BREATH
Mode.WAVE
Mode.NEON
Mode.ZOOM
Mode.SHIFTING
```

### Direction Enum

```python
from nitroglyph import Direction
```

Available directions:

```python
Direction.LEFT_TO_RIGHT
Direction.RIGHT_TO_LEFT
```

---

### effect()

Low-level effect API.

```python
ngc.effect(
    mode=Mode.BREATH,
    color=(255, 0, 0),
    speed=4,
    brightness=100,
    direction=Direction.RIGHT_TO_LEFT,
    duration=5
)
```

Parameters:

* `mode` — Effect mode
* `color` — `(R, G, B)` tuple
* `speed` — Effect speed
* `brightness` — Brightness percentage
* `direction` — Animation direction
* `duration` — Automatically clear effect after N seconds

---

### breath()

```python
ngc.breath(
    color=(255, 0, 0),
    speed=4,
    brightness=100
)
```

Example:

```python
ngc.breath(
    color=(0, 0, 255),
    duration=5
)
```

---

### wave()

```python
ngc.wave(
    speed=4,
    brightness=100,
    direction=Direction.RIGHT_TO_LEFT
)
```

Example:

```python
ngc.wave(
    direction=Direction.LEFT_TO_RIGHT,
    duration=10
)
```

---

### neon()

```python
ngc.neon(
    speed=4,
    brightness=100
)
```

Example:

```python
ngc.neon(duration=5)
```

---

### zoom()

```python
ngc.zoom(
    color=(255, 255, 255),
    speed=4,
    brightness=100
)
```

Example:

```python
ngc.zoom(
    color=(0, 255, 0),
    duration=5
)
```

---

### shifting()

```python
ngc.shifting(
    color=(255, 0, 0),
    speed=4,
    brightness=100,
    direction=Direction.RIGHT_TO_LEFT
)
```

Example:

```python
ngc.shifting(
    color=(255, 0, 255),
    direction=Direction.LEFT_TO_RIGHT,
    duration=10
)
```

---

## Example: Multi-Zone Setup

```python
from nitroglyph import NitroGlyphController

ngc = NitroGlyphController()

ngc.enable()

ngc.set_zone(1, 255, 0, 0)
ngc.set_zone(2, 0, 255, 0)
ngc.set_zone(3, 0, 0, 255)
ngc.set_zone(4, 255, 255, 255)

ngc.close()
```

---

## Example: Temporary Effect

```python
from nitroglyph import (
    NitroGlyphController,
    Direction
)

ngc = NitroGlyphController()

ngc.enable()

ngc.shifting(
    color=(255, 0, 0),
    brightness=80,
    direction=Direction.RIGHT_TO_LEFT,
    duration=5
)

ngc.close()
```

---

## Exceptions

### InvalidZoneError

Raised when an invalid zone number is supplied.

```python
ngc.set_zone(
    zone=5,
    red=255,
    green=0,
    blue=0
)
```

---

## License

MIT License
