from nitroglyph import NitroGlyphController
from time import sleep

ngc = NitroGlyphController()

COLOR = dict(red=255, green=172, blue=28)


def zone(z, b):
    ngc.set_zone(zone=z, brightness=b, **COLOR)


def play(steps, repeat=1, delay=0.1):
    for _ in range(repeat):
        for z, b in steps:
            zone(z, b)
            sleep(delay)


ngc.clear()

# Sweep
play([
    (1, 100),
    (2, 100),
    (3, 100),
    (4, 100),
    (4, 0),
    (3, 0),
    (2, 0),
], repeat=5)

# Hold zones 1 & 2 while sweeping 3 & 4
for _ in range(5):
    zone(1, 100)
    zone(2, 100)

    play([
        (3, 100),
        (4, 100),
        (4, 0),
        (3, 0),
    ])

# Hold zones 1, 2 & 3 while pulsing 4
for _ in range(5):
    zone(1, 100)
    zone(2, 100)
    zone(3, 100)

    play([
        (4, 100),
        (4, 0),
    ])

zone(0, 100)

ngc.breath(
    color=(255, 172, 28),
    speed=8,
    brightness=100,
    duration=4
)

ngc.set_zone(
    zone=0,
    red=255,
    green=191,
    blue=0,
    brightness=100
)

sleep(1)

ngc.clear()