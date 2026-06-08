import fcntl

NITRO_MAGIC = ord("N")

# These constants match the Linux ioctl bit layout.
_IOC_NRBITS = 8
_IOC_TYPEBITS = 8
_IOC_SIZEBITS = 14
_IOC_DIRBITS = 2

_IOC_NRSHIFT = 0
_IOC_TYPESHIFT = _IOC_NRSHIFT + _IOC_NRBITS
_IOC_SIZESHIFT = _IOC_TYPESHIFT + _IOC_TYPEBITS
_IOC_DIRSHIFT = _IOC_SIZESHIFT + _IOC_SIZEBITS

_IOC_NONE = 0
_IOC_WRITE = 1


def _IOC(direction, type_, nr, size):
    """Pack the ioctl fields into the integer format expected by the kernel."""
    return (
        (direction << _IOC_DIRSHIFT)
        | (type_ << _IOC_TYPESHIFT)
        | (nr << _IOC_NRSHIFT)
        | (size << _IOC_SIZESHIFT)
    )


def _IO(type_, nr):
    """Build a read-only ioctl command with no payload."""
    return _IOC(_IOC_NONE, type_, nr, 0)


def _IOW(type_, nr, size):
    """Build a write ioctl command that sends a payload of the given size."""
    return _IOC(_IOC_WRITE, type_, nr, size)


# Payload sizes must match the packed structs defined in driver/nitro_glyph.h.
ZONE_STRUCT_SIZE = 4
EFFECT_STRUCT_SIZE = 8

# Command numbers 1-4 mirror the driver header.
NITRO_IOCTL_ENABLE = _IO(NITRO_MAGIC, 1)
NITRO_IOCTL_SET_ZONE = _IOW(NITRO_MAGIC, 2, ZONE_STRUCT_SIZE)
NITRO_IOCTL_SET_EFFECT = _IOW(NITRO_MAGIC, 3, EFFECT_STRUCT_SIZE)
NITRO_IOCTL_DISABLE = _IO(NITRO_MAGIC, 4)