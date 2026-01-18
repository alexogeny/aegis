#!/bin/bash
#
# Run Aegis GTK unit tests on Ubuntu/Debian systems
#
# Usage:
#   ./scripts/run_tests.sh           # Run all tests
#   ./scripts/run_tests.sh -v        # Run with verbose output
#   ./scripts/run_tests.sh -k theme  # Run only theme tests
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Aegis GTK Test Runner ===${NC}"
echo ""

# Check for required dependencies
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

    # Check for pytest (can be installed via apt, pip, or uv)
    if ! command -v pytest &>/dev/null && ! python3 -c "import pytest" 2>/dev/null; then
        echo -e "${RED}Missing pytest${NC}"
        echo ""
        echo -e "${YELLOW}Install with one of:${NC}"
        echo "  sudo apt install python3-pytest"
        echo "  pip install pytest"
        echo "  uv tool install pytest"
        exit 1
    fi

    echo -e "${GREEN}All dependencies found.${NC}"
}

# Run tests
run_tests() {
    echo ""
    echo -e "${GREEN}Running tests...${NC}"
    echo ""

    cd "$PROJECT_ROOT"

    # Set PYTHONPATH to include the library
    export PYTHONPATH="$PROJECT_ROOT/archiso/airootfs/usr/local/lib/python3/dist-packages:$PYTHONPATH"

    # Run pytest with any passed arguments
    # Try command first (uv tool), then module
    if command -v pytest &>/dev/null; then
        pytest tests/ "$@"
    else
        python3 -m pytest tests/ "$@"
    fi
}

# Main
check_dependencies
run_tests "$@"
