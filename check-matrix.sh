#!/bin/bash
# Pre-start health check for the LED matrix driver.
# If the rgbmatrix Python bindings are missing or broken, reinstalls them
# via install.sh before the scoreboard service starts.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$SCRIPT_DIR/venv/bin/python3"
LOG="$SCRIPT_DIR/logs/mlbled.log"

check_matrix() {
    "$PYTHON" -c "from rgbmatrix import RGBMatrix, RGBMatrixOptions" 2>/dev/null
}

if check_matrix; then
    echo "$(date): [check-matrix] rgbmatrix OK" >> "$LOG"
    exit 0
fi

echo "$(date): [check-matrix] rgbmatrix import failed — running install.sh to rebuild" >> "$LOG"
cd "$SCRIPT_DIR" && sudo ./install.sh -c --force >> "$LOG" 2>&1
echo "$(date): [check-matrix] install.sh done (exit $?)" >> "$LOG"
exit 0
