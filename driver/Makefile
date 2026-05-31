obj-m += nitro_glyph.o

KDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	$(MAKE) -C $(KDIR) M=$(PWD) modules

clean:
	$(MAKE) -C $(KDIR) M=$(PWD) clean

install:
	sudo rmmod nitro_glyph 2>/dev/null || true
	sudo insmod nitro_glyph.ko

uninstall:
	sudo rmmod nitro_glyph

reload:
	sudo rmmod nitro_glyph 2>/dev/null || true
	sudo insmod nitro_glyph.ko

logs:
	dmesg | tail -50

status:
	lsmod | grep nitro || true
	ls -l /dev/nitro-glyph || true