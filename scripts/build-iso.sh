#!/usr/bin/env bash
# Aegis Linux - ISO Build Script
# =============================================================================
# This script builds the Aegis Linux ISO using archiso
# =============================================================================

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PROFILE_DIR="$PROJECT_ROOT/archiso"
WORK_DIR="/tmp/aegis-build"
OUTPUT_DIR="$PROJECT_ROOT/out"

# Print colored message
print_msg() {
    local color="$1"
    local msg="$2"
    echo -e "${color}[Aegis]${NC} $msg"
}

# Check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        print_msg "$RED" "This script must be run as root"
        exit 1
    fi
}

# Check dependencies
check_deps() {
    print_msg "$BLUE" "Checking dependencies..."

    local deps=("archiso" "pacman" "squashfs-tools" "mkinitcpio")
    local missing=()

    for dep in "${deps[@]}"; do
        if ! pacman -Qi "$dep" &>/dev/null; then
            missing+=("$dep")
        fi
    done

    if [[ ${#missing[@]} -gt 0 ]]; then
        print_msg "$YELLOW" "Installing missing dependencies: ${missing[*]}"
        pacman -S --noconfirm "${missing[@]}"
    fi

    print_msg "$GREEN" "All dependencies satisfied"
}

# Import GPG keys for custom repositories
import_keys() {
    print_msg "$BLUE" "Importing GPG keys for repositories..."

    # ArchZFS key
    if ! pacman-key --list-keys F75D9D76 &>/dev/null; then
        print_msg "$YELLOW" "Importing ArchZFS key..."
        curl -L https://archzfs.com/archzfs.gpg | pacman-key -a -
        pacman-key --lsign-key F75D9D76
    fi

    # Chaotic-AUR key
    if ! pacman-key --list-keys 3056513887B78AEB &>/dev/null; then
        print_msg "$YELLOW" "Importing Chaotic-AUR key..."
        pacman-key --recv-key 3056513887B78AEB --keyserver keyserver.ubuntu.com
        pacman-key --lsign-key 3056513887B78AEB
    fi

    # Install Chaotic-AUR keyring and mirrorlist if not present
    if ! pacman -Qi chaotic-keyring &>/dev/null; then
        pacman -U --noconfirm 'https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-keyring.pkg.tar.zst'
    fi

    if ! pacman -Qi chaotic-mirrorlist &>/dev/null; then
        pacman -U --noconfirm 'https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-mirrorlist.pkg.tar.zst'
    fi

    print_msg "$GREEN" "GPG keys imported"
}

# Clean up previous build
cleanup() {
    print_msg "$BLUE" "Cleaning up previous build..."

    if [[ -d "$WORK_DIR" ]]; then
        # Check for mounted filesystems
        if mount | grep -q "$WORK_DIR"; then
            print_msg "$YELLOW" "Unmounting filesystems in work directory..."
            umount -R "$WORK_DIR" 2>/dev/null || true
        fi
        rm -rf "$WORK_DIR"
    fi

    print_msg "$GREEN" "Cleanup complete"
}

# Prepare build environment
prepare() {
    print_msg "$BLUE" "Preparing build environment..."

    mkdir -p "$WORK_DIR"
    mkdir -p "$OUTPUT_DIR"

    # Ensure profile directory exists
    if [[ ! -d "$PROFILE_DIR" ]]; then
        print_msg "$RED" "Profile directory not found: $PROFILE_DIR"
        exit 1
    fi

    # Verify essential files
    local essential_files=(
        "profiledef.sh"
        "pacman.conf"
        "packages.x86_64"
    )

    for file in "${essential_files[@]}"; do
        if [[ ! -f "$PROFILE_DIR/$file" ]]; then
            print_msg "$RED" "Essential file missing: $file"
            exit 1
        fi
    done

    print_msg "$GREEN" "Build environment ready"
}

# Build the ISO
build_iso() {
    print_msg "$BLUE" "Building Aegis Linux ISO..."
    print_msg "$YELLOW" "This may take a while..."

    mkarchiso -v \
        -w "$WORK_DIR" \
        -o "$OUTPUT_DIR" \
        "$PROFILE_DIR"

    local iso_file
    iso_file=$(find "$OUTPUT_DIR" -maxdepth 1 -name 'aegis-*.iso' -printf '%T@ %p\n' 2>/dev/null | sort -rn | head -1 | cut -d' ' -f2-)

    if [[ -n "$iso_file" ]]; then
        print_msg "$GREEN" "Build successful!"
        print_msg "$GREEN" "ISO: $iso_file"
        print_msg "$GREEN" "Size: $(du -h "$iso_file" | cut -f1)"

        # Generate checksums
        print_msg "$BLUE" "Generating checksums..."
        cd "$OUTPUT_DIR"
        sha256sum "$(basename "$iso_file")" > "$(basename "$iso_file").sha256"
        b2sum "$(basename "$iso_file")" > "$(basename "$iso_file").b2sum"
        print_msg "$GREEN" "Checksums generated"
    else
        print_msg "$RED" "Build failed - no ISO found!"
        exit 1
    fi
}

# Main function
main() {
    print_msg "$BLUE" "====================================="
    print_msg "$BLUE" "    Aegis Linux ISO Builder"
    print_msg "$BLUE" "====================================="

    check_root
    check_deps
    import_keys
    cleanup
    prepare
    build_iso

    print_msg "$GREEN" "====================================="
    print_msg "$GREEN" "    Build Complete!"
    print_msg "$GREEN" "====================================="
}

# Handle script arguments
case "${1:-}" in
    clean)
        check_root
        cleanup
        print_msg "$GREEN" "Cleaned up build artifacts"
        ;;
    help|--help|-h)
        echo "Aegis Linux ISO Builder"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  (none)   Build the ISO"
        echo "  clean    Clean up build artifacts"
        echo "  help     Show this help message"
        ;;
    *)
        main
        ;;
esac
