#!/usr/bin/env bash
# Aegis Linux - Build ISO in Container
# Use this when not on an Arch Linux host
# =============================================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[OK]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Detect container runtime
if command -v podman &>/dev/null; then
    RUNTIME="podman"
elif command -v docker &>/dev/null; then
    RUNTIME="docker"
else
    log_error "Neither podman nor docker found. Please install one."
    exit 1
fi

log_info "Using container runtime: $RUNTIME"

# Check if running with sufficient privileges
if [[ "$RUNTIME" == "docker" ]] && ! docker info &>/dev/null; then
    log_error "Docker is not running or you don't have permission."
    log_info "Try: sudo usermod -aG docker \$USER && newgrp docker"
    exit 1
fi

# Create output directory
OUTPUT_DIR="$PROJECT_DIR/out"
mkdir -p "$OUTPUT_DIR"

log_info "Building Aegis Linux ISO in container..."
log_info "Project directory: $PROJECT_DIR"
log_info "Output directory: $OUTPUT_DIR"

# Build command - must set up repos BEFORE building
BUILD_CMD='
set -e
echo "=== Initializing pacman keyring ==="
pacman-key --init
pacman-key --populate archlinux

echo "=== Updating system ==="
pacman -Syu --noconfirm

echo "=== Installing base tools ==="
pacman -S --noconfirm --needed archiso git base-devel

echo "=== Setting up Chaotic-AUR repository ==="
# Import and sign the key
pacman-key --recv-key 3056513887B78AEB --keyserver keyserver.ubuntu.com
pacman-key --lsign-key 3056513887B78AEB

# Install chaotic-keyring and mirrorlist
pacman -U --noconfirm "https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-keyring.pkg.tar.zst"
pacman -U --noconfirm "https://cdn-mirror.chaotic.cx/chaotic-aur/chaotic-mirrorlist.pkg.tar.zst"

# Add chaotic-aur to pacman.conf (for the build host)
if ! grep -q "chaotic-aur" /etc/pacman.conf; then
    echo "" >> /etc/pacman.conf
    echo "[chaotic-aur]" >> /etc/pacman.conf
    echo "Include = /etc/pacman.d/chaotic-mirrorlist" >> /etc/pacman.conf
fi

echo "=== Setting up ArchZFS repository ==="
# Import archzfs key
pacman-key --recv-keys DDF7DB817396A49B2A2723F7403BD972F75D9D76 --keyserver keyserver.ubuntu.com
pacman-key --lsign-key DDF7DB817396A49B2A2723F7403BD972F75D9D76

# Add archzfs mirrorlist
cat > /etc/pacman.d/archzfs-mirrorlist << "MIRROREOF"
Server = https://archzfs.com/$repo/$arch
Server = https://mirror.sum7.eu/archlinux/archzfs/$repo/$arch
Server = https://mirror.biocrafting.net/archlinux/archzfs/$repo/$arch
MIRROREOF

# Add archzfs to pacman.conf
if ! grep -q "archzfs" /etc/pacman.conf; then
    echo "" >> /etc/pacman.conf
    echo "[archzfs]" >> /etc/pacman.conf
    echo "Include = /etc/pacman.d/archzfs-mirrorlist" >> /etc/pacman.conf
fi

# Refresh package databases
pacman -Sy

echo "=== Verifying repositories ==="
pacman -Sl chaotic-aur | head -5
pacman -Sl archzfs | head -5

echo "=== Building Calamares from AUR ==="
# Create a build user (makepkg cannot run as root)
useradd -m builder
echo "builder ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers

# Install calamares build dependencies
pacman -S --noconfirm --needed cmake extra-cmake-modules qt6-base qt6-declarative qt6-tools \
    qt6-translations kpmcore yaml-cpp boost libpwquality icu polkit-qt6 \
    kconfig kcoreaddons ki18n kiconthemes kio kparts kservice kwidgetsaddons \
    python squashfs-tools appstream-qt plasma5support

# Build calamares as builder user
cd /tmp
sudo -u builder git clone https://aur.archlinux.org/calamares.git
cd calamares
sudo -u builder makepkg -s --noconfirm || {
    echo "Calamares build failed, will use archinstall as fallback"
}

# Install if built successfully
CALAMARES_BUILT=false
if ls *.pkg.tar.zst 1>/dev/null 2>&1; then
    pacman -U --noconfirm *.pkg.tar.zst
    mkdir -p /tmp/localrepo
    cp *.pkg.tar.zst /tmp/localrepo/
    cd /tmp/localrepo
    repo-add localrepo.db.tar.gz *.pkg.tar.zst
    CALAMARES_BUILT=true
    echo "Calamares built and ready"
else
    echo "WARNING: Calamares not available, archinstall will be the installer"
fi

echo "=== Building ISO ==="

# Create a working copy of the archiso profile
cp -r /aegis/archiso /tmp/aegis-profile
cd /tmp/aegis-profile

# Create work directory
mkdir -p /tmp/aegis-work /aegis/out

# If calamares was built, add local repo to the COPY of pacman.conf
if [ "$CALAMARES_BUILT" = true ]; then
    echo "" >> /tmp/aegis-profile/pacman.conf
    echo "[localrepo]" >> /tmp/aegis-profile/pacman.conf
    echo "SigLevel = Optional TrustAll" >> /tmp/aegis-profile/pacman.conf
    echo "Server = file:///tmp/localrepo" >> /tmp/aegis-profile/pacman.conf

    # Add calamares to the COPY of packages list
    echo "calamares" >> /tmp/aegis-profile/packages.x86_64
fi

# Build the ISO from the working copy
mkarchiso -v -w /tmp/aegis-work -o /aegis/out /tmp/aegis-profile

echo "=== Build complete ==="
ls -lh /aegis/out/*.iso
'

# Run the build
$RUNTIME run -it --rm \
    --privileged \
    -v "$PROJECT_DIR:/aegis:z" \
    archlinux:latest \
    /bin/bash -c "$BUILD_CMD"

if [[ $? -eq 0 ]]; then
    log_success "Build completed!"
    log_info "ISO location: $OUTPUT_DIR/"
    ls -lh "$OUTPUT_DIR"/*.iso 2>/dev/null || log_warn "No ISO found - check build output"
else
    log_error "Build failed"
    exit 1
fi
