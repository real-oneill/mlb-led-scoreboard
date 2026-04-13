#!/bin/bash
# Pre-start health check for the LED matrix driver.
# Detects corruption via SHA256 checksum and Python import test.
# If either fails, deletes the submodule and does a full reinstall.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$SCRIPT_DIR/venv/bin/python3"
LOG="$SCRIPT_DIR/logs/mlbled.log"
SO_DIR="$SCRIPT_DIR/submodules/matrix/bindings/python/rgbmatrix"
CHECKSUM_FILE="$SCRIPT_DIR/.rgbmatrix-so-checksum"

reinstall() {
    echo "$(date): [check-matrix] $1 — deleting submodule and reinstalling" >> "$LOG"
    sudo rm -rf "$SCRIPT_DIR/submodules/matrix"
    cd "$SCRIPT_DIR" && sudo ./install.sh -c --force >> "$LOG" 2>&1
    echo "$(date): [check-matrix] install.sh done (exit $?)" >> "$LOG"
    sha256sum "$SO_DIR"/*.so > "$CHECKSUM_FILE" 2>/dev/null
}

check_import() {
    "$PYTHON" -c "from rgbmatrix import RGBMatrix, RGBMatrixOptions" 2>/dev/null
}

# Step 1: .so must exist
if ! ls "$SO_DIR"/*.so >/dev/null 2>&1; then
    reinstall ".so not found"
fi

# Step 2: checksum verification — catches corrupted .so that still imports
if [ -f "$CHECKSUM_FILE" ]; then
    if ! sha256sum --check "$CHECKSUM_FILE" --quiet 2>/dev/null; then
        reinstall "checksum mismatch — .so corrupted since last good build"
    fi
else
    # First run: no baseline yet — save current .so checksum
    sha256sum "$SO_DIR"/*.so > "$CHECKSUM_FILE" 2>/dev/null
    echo "$(date): [check-matrix] saved initial .so checksum baseline" >> "$LOG"
fi

# Step 3: Python import test
if ! check_import; then
    reinstall "rgbmatrix import failed"
fi

echo "$(date): [check-matrix] rgbmatrix OK (checksum + import)" >> "$LOG"
exit 0
