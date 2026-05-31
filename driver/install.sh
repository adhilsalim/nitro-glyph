#!/usr/bin/env bash
set -e

make clean
make

sudo rmmod nitro_glyph 2>/dev/null || true

sudo insmod nitro_glyph.ko

echo "Installed nitro_glyph"
