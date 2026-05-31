#ifndef NITRO_GLYPH_H
#define NITRO_GLYPH_H

#include <linux/ioctl.h>
#include <linux/types.h>

#define NITRO_MAGIC 'N'

enum nitro_mode {
    NITRO_STATIC   = 0,
    NITRO_BREATH   = 1,
    NITRO_NEON     = 2,
    NITRO_WAVE     = 3,
    NITRO_SHIFTING = 4,
    NITRO_ZOOM     = 5
};

struct nitro_zone {
    __u8 zone;      /* 1..4 */
    __u8 red;
    __u8 green;
    __u8 blue;
};

struct nitro_effect {
    __u8 mode;
    __u8 speed;
    __u8 brightness;
    __u8 direction;
    __u8 red;
    __u8 green;
    __u8 blue;
    __u8 reserved;
};

#define NITRO_IOCTL_ENABLE \
    _IO(NITRO_MAGIC, 1)

#define NITRO_IOCTL_SET_ZONE \
    _IOW(NITRO_MAGIC, 2, struct nitro_zone)

#define NITRO_IOCTL_SET_EFFECT \
    _IOW(NITRO_MAGIC, 3, struct nitro_effect)

#define NITRO_IOCTL_DISABLE \
    _IO(NITRO_MAGIC, 4)

#endif