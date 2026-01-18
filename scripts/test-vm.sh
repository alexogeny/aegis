#!/usr/bin/env bash
# Aegis Linux - VM Test Script
# =============================================================================
# Launch the ISO in QEMU for testing
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="$PROJECT_ROOT/out"

# Find the latest ISO
if [[ -n "${1:-}" ]]; then
    ISO_PATH="$1"
else
    ISO_PATH=$(find "$OUTPUT_DIR" -maxdepth 1 -name 'aegis-*.iso' -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)
fi

if [[ ! -f "$ISO_PATH" ]]; then
    echo "Error: No ISO found. Build one first with: sudo ./scripts/build-iso.sh"
    exit 1
fi

echo "Testing ISO: $ISO_PATH"

# Check for OVMF (UEFI firmware)
OVMF_PATHS=(
    "/usr/share/edk2/x64/OVMF.4m.fd"
    "/usr/share/ovmf/x64/OVMF.fd"
    "/usr/share/edk2-ovmf/x64/OVMF_CODE.fd"
    "/usr/share/OVMF/OVMF_CODE.fd"
)

OVMF_PATH=""
for path in "${OVMF_PATHS[@]}"; do
    if [[ -f "$path" ]]; then
        OVMF_PATH="$path"
        break
    fi
done

# Create test disk if it doesn't exist
TEST_DISK="$OUTPUT_DIR/test-disk.qcow2"
if [[ ! -f "$TEST_DISK" ]]; then
    echo "Creating test disk..."
    qemu-img create -f qcow2 "$TEST_DISK" 50G
fi

# QEMU arguments
QEMU_ARGS=(
    -enable-kvm
    -m 8G
    -cpu host
    -smp "4,sockets=1,cores=4,threads=1"
    -drive "file=$ISO_PATH,media=cdrom,readonly=on"
    -drive "file=$TEST_DISK,if=virtio,format=qcow2"
    -device "virtio-net-pci,netdev=net0"
    -netdev "user,id=net0,hostfwd=tcp::2222-:22"
    -device ich9-intel-hda
    -device hda-duplex
    -usb
    -device usb-tablet
)

# Add UEFI firmware if available
if [[ -n "$OVMF_PATH" ]]; then
    echo "Using UEFI firmware: $OVMF_PATH"
    QEMU_ARGS+=(-bios "$OVMF_PATH")
else
    echo "Warning: OVMF not found, using BIOS mode"
    echo "Install edk2-ovmf for UEFI testing"
fi

# Graphics options
if [[ "${DISPLAY:-}" ]]; then
    # GUI mode with virtio-vga-gl for better performance
    QEMU_ARGS+=(
        -device virtio-vga-gl
        -display "gtk,gl=on"
    )
else
    # Headless mode with VNC
    echo "No display detected, using VNC on :0 (port 5900)"
    QEMU_ARGS+=(
        -device virtio-vga
        -vnc :0
    )
fi

echo "Starting QEMU..."
echo "SSH will be available at localhost:2222 after OS starts"
echo ""

qemu-system-x86_64 "${QEMU_ARGS[@]}"
