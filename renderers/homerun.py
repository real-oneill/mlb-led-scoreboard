"""
renderers/homerun.py
--------------------
Renders the home run celebration on the LED matrix.
- Scrolls "[TEAM NAME] HOME RUN!" across the full display
- Cycles base runner diamonds during the scroll (reusing existing base rendering)
- Runs for a fixed duration then returns control to the main render loop

Uses the same graphics primitives and layout system as the rest of the scoreboard.
"""

import time
import debug
from driver import graphics


# How long the animation plays in seconds
HR_ANIMATION_DURATION = 8

# Scroll speed — lower = faster
SCROLL_DELAY = 0.02


def render_homerun_celebration(matrix, layout, colors, team_name, font_key="atbat.batter"):
    """
    Main entry point. Call this from the game renderer when a home run is detected.

    Args:
        matrix:     The RGBMatrix instance
        layout:     Layout object (for coords and fonts)
        colors:     Color object (for graphics colors)
        team_name:  Full team name string e.g. "White Sox", "Cubs"
        font_key:   Font to use for scrolling text (defaults to batter font)
    """
    try:
        font = layout.font(font_key)
        text_color = graphics.Color(255, 255, 255)   # white text
        bg_color   = colors.graphics_color("default.background")
        base_color = graphics.Color(255, 200, 0)     # gold bases

        text = f"  {team_name.upper()} HOME RUN!  "
        char_width = font["size"]["width"]
        text_pixel_width = char_width * len(text)

        # Base cycling sequence — cycles through which bases are "lit"
        # during the animation to look like runners going around
        bases_sequence = [
            [True,  False, False],   # runner on 1st
            [False, True,  False],   # runner on 2nd
            [False, False, True],    # runner on 3rd
            [True,  True,  False],   # 1st and 2nd
            [False, True,  True],    # 2nd and 3rd
            [True,  True,  True],    # bases loaded
            [True,  False, True],    # corners
        ]

        # Get base pixel coords from layout (same as normal game rendering)
        base_px = [
            layout.coords("bases.1B"),
            layout.coords("bases.2B"),
            layout.coords("bases.3B"),
        ]
        base_colors = [
            colors.graphics_color("bases.1B"),
            colors.graphics_color("bases.2B"),
            colors.graphics_color("bases.3B"),
        ]

        offscreen = matrix.CreateFrameCanvas()
        x_pos = matrix.width
        start = time.time()

        while time.time() - start < HR_ANIMATION_DURATION:
            offscreen.Clear()

            # ── Scrolling text ──────────────────────────────────────
            graphics.DrawText(offscreen, font["font"], x_pos, 10, text_color, text)
            x_pos -= 1
            if x_pos < -text_pixel_width:
                x_pos = matrix.width  # loop the scroll

            # ── Cycling base runners ────────────────────────────────
            cycle_idx = int((time.time() - start) / 0.35) % len(bases_sequence)
            runners = bases_sequence[cycle_idx]

            for i in range(3):
                _render_base_outline(offscreen, base_px[i], base_colors[i])
                if runners[i]:
                    _render_baserunner(offscreen, base_px[i], base_color)

            offscreen = matrix.SwapOnVSync(offscreen)
            time.sleep(SCROLL_DELAY)

        # Clear the canvas when done
        offscreen.Clear()
        matrix.SwapOnVSync(offscreen)

    except Exception as e:
        debug.error(f"Home run animation error: {e}")


# ── Base drawing helpers (mirrors game.py exactly) ──────────────────────────

def _render_base_outline(canvas, base, color):
    x, y = base["x"], base["y"]
    size = base["size"]
    half = abs(size // 2)
    graphics.DrawLine(canvas, x + half, y,        x,        y + half, color)
    graphics.DrawLine(canvas, x + half, y,        x + size, y + half, color)
    graphics.DrawLine(canvas, x + half, y + size, x,        y + half, color)
    graphics.DrawLine(canvas, x + half, y + size, x + size, y + half, color)


def _render_baserunner(canvas, base, color):
    x, y = base["x"], base["y"]
    size = base["size"]
    half = abs(size // 2)
    for offset in range(1, half + 1):
        graphics.DrawLine(canvas, x + half - offset, y + size - offset,
                                  x + half + offset, y + size - offset, color)
        graphics.DrawLine(canvas, x + half - offset, y + offset,
                                  x + half + offset, y + offset,         color)
