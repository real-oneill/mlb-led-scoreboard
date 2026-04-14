#!/bin/bash
# Pre-start health check: verify rgbmatrix bindings load correctly.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PYTHON="$SCRIPT_DIR/venv/bin/python3"
LOG="$SCRIPT_DIR/logs/mlbled.log"

if ! "$PYTHON" -c "from rgbmatrix import RGBMatrix, RGBMatrixOptions" 2>/dev/null; then
    echo "$(date): [check-matrix] rgbmatrix import failed — service will not start" >> "$LOG"
    exit 1
fi

echo "$(date): [check-matrix] rgbmatrix OK" >> "$LOG"
exit 0
