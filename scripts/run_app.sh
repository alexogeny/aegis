#!/bin/bash
#
# Run Aegis GTK applications on Ubuntu/Debian systems
#
# Usage:
#   ./scripts/run_app.sh lighting    # Run aegis-lighting
#   ./scripts/run_app.sh macropad    # Run aegis-macropad
#   ./scripts/run_app.sh armor       # Run aegis-armor
#   ./scripts/run_app.sh --list      # List all available apps
#
# This script sets up the Python path to include the aegis_gtk library
# and runs the specified application.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
BIN_DIR="$PROJECT_ROOT/archiso/airootfs/usr/local/bin"
LIB_DIR="$PROJECT_ROOT/archiso/airootfs/usr/local/lib/python3/dist-packages"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Available apps
APPS=(
    "lighting:aegis-lighting:Elgato Key Light controller"
    "macropad:aegis-macropad:Stream Deck-style macro buttons"
    "armor:aegis-armor:Security and firewall settings"
    "backup:aegis-backup:Backup management"
    "displays:aegis-displays:Display configuration"
    "mixer:aegis-mixer:Audio mixer"
    "updates:aegis-updates:System updates"
    "welcome:aegis-welcome:Welcome screen"
    "containers:aegis-containers:Docker/Podman container manager"
    "clipboard:aegis-clipboard:Clipboard history manager"
)

show_help() {
    echo -e "${GREEN}=== Aegis GTK App Runner ===${NC}"
    echo ""
    echo "Run Aegis GTK applications on Ubuntu/Debian for development and testing."
    echo ""
    echo -e "${CYAN}Usage:${NC}"
    echo "  $0 <app-name>     Run the specified app"
    echo "  $0 --list         List all available apps"
    echo "  $0 --help         Show this help"
    echo ""
    echo -e "${CYAN}Available apps:${NC}"
    for app_info in "${APPS[@]}"; do
        IFS=':' read -r name binary desc <<< "$app_info"
        printf "  ${GREEN}%-12s${NC} %s\n" "$name" "$desc"
    done
    echo ""
    echo -e "${CYAN}Examples:${NC}"
    echo "  $0 lighting       # Run the lighting app"
    echo "  $0 macropad       # Run the macropad app"
    echo ""
}

list_apps() {
    echo -e "${GREEN}Available Aegis GTK Apps:${NC}"
    echo ""
    for app_info in "${APPS[@]}"; do
        IFS=':' read -r name binary desc <<< "$app_info"
        printf "  ${CYAN}%-12s${NC} %-20s %s\n" "$name" "($binary)" "$desc"
    done
    echo ""
}

check_dependencies() {
    local missing=()

    if ! python3 -c "import gi" 2>/dev/null; then
        missing+=("python3-gi")
    fi

    if ! python3 -c "gi.require_version('Gtk', '4.0'); from gi.repository import Gtk" 2>/dev/null; then
        missing+=("gir1.2-gtk-4.0")
    fi

    if ! python3 -c "gi.require_version('Adw', '1'); from gi.repository import Adw" 2>/dev/null; then
        missing+=("gir1.2-adw-1")
    fi

    if [ ${#missing[@]} -gt 0 ]; then
        echo -e "${RED}Missing dependencies:${NC}"
        for dep in "${missing[@]}"; do
            echo "  - $dep"
        done
        echo ""
        echo -e "${YELLOW}Install with:${NC}"
        echo "  sudo apt install ${missing[*]}"
        exit 1
    fi
}

find_app() {
    local search="$1"

    for app_info in "${APPS[@]}"; do
        IFS=':' read -r name binary desc <<< "$app_info"
        if [ "$name" = "$search" ]; then
            echo "$binary"
            return 0
        fi
    done

    return 1
}

run_app() {
    local app_name="$1"
    local binary

    if ! binary=$(find_app "$app_name"); then
        echo -e "${RED}Error: Unknown app '$app_name'${NC}"
        echo ""
        echo "Run '$0 --list' to see available apps."
        exit 1
    fi

    local app_path="$BIN_DIR/$binary"

    if [ ! -f "$app_path" ]; then
        echo -e "${RED}Error: App binary not found at $app_path${NC}"
        exit 1
    fi

    echo -e "${GREEN}Running $binary...${NC}"
    echo ""

    # Set up environment
    export PYTHONPATH="$LIB_DIR:$PYTHONPATH"

    # Run the app
    python3 "$app_path"
}

# Main
if [ $# -eq 0 ]; then
    show_help
    exit 0
fi

case "$1" in
    --help|-h)
        show_help
        exit 0
        ;;
    --list|-l)
        list_apps
        exit 0
        ;;
    *)
        check_dependencies
        run_app "$1"
        ;;
esac
