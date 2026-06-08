"""
pinwheel_leds.py
----------------
Controls the 7 pinwheel LEDs wired to the Pi's free GPIO pins.
Place this file in the mlb-led-scoreboard repo root.

Pin order (left → right across the scoreboard pinwheels):
    Pinwheel 1 → GPIO 25  (bonnet pad: 25)
    Pinwheel 2 → GPIO 10  (bonnet pad: MO / MOSI)
    Pinwheel 3 → GPIO 9   (bonnet pad: MI / MISO)
    Pinwheel 4 → GPIO 11  (bonnet pad: CLK / SCLK)
    Pinwheel 5 → GPIO 8   (bonnet pad: CE0)
    Pinwheel 6 → GPIO 7   (bonnet pad: CE1)
    Pinwheel 7 → GPIO 19  (bonnet pad: 19)
    GND        → bonnet GND pad near TX/RX
"""

import threading
import time
import debug

PI_PINS_BCM = [25, 10, 9, 11, 8, 7, 19]

try:
    import RPi.GPIO as GPIO
    _MOCK = False
except ImportError:
    _MOCK = True
    debug.warning("RPi.GPIO not found — pinwheel LEDs running in mock mode")

_initialized = False


def setup():
    """Call once at scoreboard startup to initialize all pins LOW."""
    global _initialized
    if _MOCK or _initialized:
        return
    try:
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        for pin in PI_PINS_BCM:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, GPIO.LOW)
        _initialized = True
        debug.log("Pinwheel LEDs initialized")
    except Exception as e:
        debug.error(f"Pinwheel LED setup failed: {e}")


def all_on():
    if _MOCK: return
    for pin in PI_PINS_BCM:
        GPIO.output(pin, GPIO.HIGH)


def all_off():
    if _MOCK: return
    for pin in PI_PINS_BCM:
        GPIO.output(pin, GPIO.LOW)


def flash(times=3, on_secs=0.2, off_secs=0.15):
    for _ in range(times):
        all_on()
        time.sleep(on_secs)
        all_off()
        time.sleep(off_secs)


def cycle_one_by_one(delay=0.18):
    if _MOCK: return
    for pin in PI_PINS_BCM:
        GPIO.output(pin, GPIO.HIGH)
        time.sleep(delay)


def home_run_sequence():
    """
    Full LED celebration:
      1. Triple burst flash
      2. Cycle on left → right (one pinwheel at a time)
      3. Hold 0.5s
      4. Five rapid flashes
      5. All off
    """
    try:
        flash(times=3, on_secs=0.2, off_secs=0.15)
        all_off()
        time.sleep(0.1)
        cycle_one_by_one(delay=0.18)
        time.sleep(0.5)
        flash(times=5, on_secs=0.12, off_secs=0.1)
    finally:
        all_off()


def trigger_async():
    """Fire the LED sequence in a background thread (non-blocking)."""
    t = threading.Thread(target=home_run_sequence, daemon=True)
    t.start()
    return t


def cleanup():
    """Call at scoreboard shutdown."""
    all_off()
    if not _MOCK and _initialized:
        GPIO.cleanup()
