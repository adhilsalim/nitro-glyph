from enum import IntEnum


class Mode(IntEnum):
    STATIC = 0
    BREATH = 1
    NEON = 2
    WAVE = 3
    SHIFTING = 4
    ZOOM = 5


class Direction(IntEnum):
    LEFT_TO_RIGHT = 1
    RIGHT_TO_LEFT = 2