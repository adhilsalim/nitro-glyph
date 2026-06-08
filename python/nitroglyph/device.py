import os
import fcntl

from .exceptions import DeviceNotFoundError

DEVICE_PATH = "/dev/nitro-glyph"


class NitroGlyphDevice:
    def __init__(self):
        if not os.path.exists(DEVICE_PATH):
            raise DeviceNotFoundError(
                f"{DEVICE_PATH} not found"
            )

        self.fd = os.open(
            DEVICE_PATH,
            os.O_RDWR
        )

    def ioctl(self, command, payload=b""):
        return fcntl.ioctl(
            self.fd,
            command,
            payload
        )

    def close(self):
        if self.fd:
            os.close(self.fd)
            self.fd = None