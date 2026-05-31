CC = gcc

CFLAGS = -Wall -Wextra -I..

all: test_enable test_zone test_effect

test_enable: test_enable.c
	$(CC) $(CFLAGS) test_enable.c -o test_enable

test_zone: test_zone.c
	$(CC) $(CFLAGS) test_zone.c -o test_zone

test_effect: test_effect.c
	$(CC) $(CFLAGS) test_effect.c -o test_effect

clean:
	rm -f test_enable test_zone test_effect

run-enable: test_enable
	sudo ./test_enable

run-zone: test_zone
	sudo ./test_zone

run-effect: test_effect
	sudo ./test_effect