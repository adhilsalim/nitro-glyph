#!/usr/bin/env bash
set -e

MODULE_NAME="nitro_glyph"
DKMS_NAME="nitro-glyph"
DKMS_VERSION="0.1.0"

sudo rmmod "$MODULE_NAME" 2>/dev/null || true

if command -v dkms >/dev/null 2>&1 && sudo dkms status "${DKMS_NAME}/${DKMS_VERSION}" 2>/dev/null | grep -q "${DKMS_NAME}"; then
    sudo dkms remove "${DKMS_NAME}/${DKMS_VERSION}" --all
    sudo rm -rf "/usr/src/${DKMS_NAME}-${DKMS_VERSION}"
else
    sudo find "/lib/modules/$(uname -r)" -name "${MODULE_NAME}.ko" -delete
    sudo depmod -a
fi

sudo rm -f "/etc/modules-load.d/${MODULE_NAME}.conf"

echo "Removed ${MODULE_NAME}"
