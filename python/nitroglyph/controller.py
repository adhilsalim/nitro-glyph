import struct
import time

from .device import NitroGlyphDevice
from .constants import (
    Mode,
    Direction,
)
from .ioctl import (
    NITRO_IOCTL_ENABLE,
    NITRO_IOCTL_SET_ZONE,
    NITRO_IOCTL_SET_EFFECT,
)
from .exceptions import (
    InvalidZoneError,
)


class NitroGlyphController:
    def __init__(self):
        self.dev = NitroGlyphDevice()

    def close(self):
        self.dev.close()

    def enable(self):
        self.dev.ioctl(
            NITRO_IOCTL_ENABLE
        )
        
    def clear(self):
        self.set_zone(
            zone=0,
            red=0,
            green=0,
            blue=0,
            brightness=0
        )

    def disable(self):
        self.clear()

    def _scale_color(self, red, green, blue, brightness):
        if brightness < 0 or brightness > 100:
            raise ValueError("Brightness must be within 0-100 (inclusive)")

        scale = brightness / 100
        return (
            int(red * scale),
            int(green * scale),
            int(blue * scale),
        )

    def set_zone(
        self,
        zone,
        red,
        green,
        blue,
        brightness=100
    ):
        if zone not in (0, 1, 2, 3, 4):
            raise InvalidZoneError(
                "Zone number must be within 0-4 (inclusive)"
            )

        red, green, blue = self._scale_color(
            red,
            green,
            blue,
            brightness
        )

        if zone == 0:
            for z in (1, 2, 3, 4):
                self.set_zone(
                    z,
                    red,
                    green,
                    blue,
                    brightness=100
                )
            return

        payload = struct.pack(
            "BBBB",
            zone,
            red,
            green,
            blue
        )

        self.dev.ioctl(
            NITRO_IOCTL_SET_ZONE,
            payload
        )

    def effect(
        self,
        mode,
        color,
        speed=4,
        brightness=100,
        direction=Direction.RIGHT_TO_LEFT,
        duration=None
    ):
        red, green, blue = color

        if mode in (Mode.WAVE, Mode.NEON):
            red = 0
            green = 0
            blue = 0

        payload = struct.pack(
            "BBBBBBBB",
            int(mode),
            speed,
            brightness,
            int(direction),
            red,
            green,
            blue,
            0
        )

        self.dev.ioctl(
            NITRO_IOCTL_SET_EFFECT,
            payload
        )

        if duration is not None:
            time.sleep(duration)
            self.clear()

    def breath(
        self,
        color,
        speed=4,
        brightness=100
    , duration=None):
        self.effect(
            Mode.BREATH,
            color,
            speed,
            brightness,
            duration=duration
        )

    def wave(
        self,
        speed=4,
        brightness=100,
        direction=Direction.RIGHT_TO_LEFT
    , duration=None):
        self.effect(
            Mode.WAVE,
            (0, 0, 0),
            speed,
            brightness,
            direction,
            duration=duration
        )

    def neon(
        self,
        speed=4,
        brightness=100
    , duration=None):
        self.effect(
            Mode.NEON,
            (0, 0, 0),
            speed,
            brightness,
            duration=duration
        )

    def zoom(
        self,
        color,
        speed=4,
        brightness=100
    , duration=None):
        self.effect(
            Mode.ZOOM,
            color,
            speed,
            brightness,
            duration=duration
        )

    def shifting(
        self,
        color,
        speed=4,
        brightness=100,
        direction=Direction.RIGHT_TO_LEFT
    , duration=None):
        self.effect(
            Mode.SHIFTING,
            color,
            speed,
            brightness,
            direction,
            duration=duration
        )