#include <stdio.h>
#include <fcntl.h>
#include <sys/ioctl.h>
#include <unistd.h>

#include "nitro_glyph.h"

int main(void)
{
    int fd;

    fd = open("/dev/nitro-glyph", O_RDWR);

    if (fd < 0) {
        perror("open");
        return 1;
    }

    ioctl(fd, NITRO_IOCTL_ENABLE);

    close(fd);

    return 0;
}