#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MODULE_NAME="nitro_glyph"
DKMS_NAME="nitro-glyph"
DKMS_VERSION="0.1.0"

if command -v mokutil >/dev/null 2>&1 && mokutil --sb-state 2>/dev/null | grep -qi "enabled"; then
    echo "WARNING: Secure Boot is enabled."
    echo "This is an unsigned out-of-tree module — it will fail to load until"
    echo "you disable Secure Boot or enroll a signing key via MOK."
    echo "See driver/SECURE_BOOT.md before continuing."
    echo
fi

if command -v dkms >/dev/null 2>&1; then
    echo "==> Installing via DKMS (rebuilds automatically on kernel updates)"

    DKMS_SRC="/usr/src/${DKMS_NAME}-${DKMS_VERSION}"

    sudo dkms remove "${DKMS_NAME}/${DKMS_VERSION}" --all >/dev/null 2>&1 || true
    sudo rm -rf "$DKMS_SRC"
    sudo mkdir -p "$DKMS_SRC"
    sudo cp "$SCRIPT_DIR/Makefile" "$SCRIPT_DIR/dkms.conf" "$SCRIPT_DIR/nitro_glyph.c" "$SCRIPT_DIR/nitro_glyph.h" "$DKMS_SRC/"

    sudo dkms add -m "$DKMS_NAME" -v "$DKMS_VERSION"
    sudo dkms build -m "$DKMS_NAME" -v "$DKMS_VERSION"
    sudo dkms install -m "$DKMS_NAME" -v "$DKMS_VERSION"
else
    echo "==> dkms not found — installing a one-off build for the running kernel only."
    echo "    It will need to be reinstalled after every kernel update. For a"
    echo "    persistent install, install dkms first:"
    echo "      Fedora:        sudo dnf install dkms"
    echo "      Debian/Ubuntu: sudo apt install dkms"
    echo

    make -C "$SCRIPT_DIR" clean
    make -C "$SCRIPT_DIR"

    DEST_DIR="/lib/modules/$(uname -r)/kernel/drivers/platform/x86"
    sudo mkdir -p "$DEST_DIR"
    sudo cp "$SCRIPT_DIR/${MODULE_NAME}.ko" "$DEST_DIR/${MODULE_NAME}.ko"
    sudo depmod -a
fi

sudo cp "$SCRIPT_DIR/${MODULE_NAME}.conf" "/etc/modules-load.d/${MODULE_NAME}.conf"

sudo rmmod "$MODULE_NAME" 2>/dev/null || true
sudo modprobe "$MODULE_NAME"

echo
echo "Installed ${MODULE_NAME} — it will now load automatically on boot"
echo "(via /etc/modules-load.d/${MODULE_NAME}.conf)."
