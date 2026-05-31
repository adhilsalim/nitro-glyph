#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/ioctl.h>

#include "nitro_glyph.h"

int main(void)
{
    int fd;

    struct nitro_effect effect = {
        .mode = NITRO_BREATH,
        .speed = 4,
        .brightness = 100,
        .direction = 1,

        .red = 0,
        .green = 255,
        .blue = 0
    };

    fd = open("/dev/nitro-glyph", O_RDWR);

    if (fd < 0) {
        perror("open");
        return 1;
    }

    if (ioctl(fd, NITRO_IOCTL_SET_EFFECT, &effect) < 0) {
        perror("ioctl");
        return 1;
    }

    close(fd);

    return 0;
}