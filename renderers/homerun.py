"""
renderers/homerun.py
--------------------
Home run celebration on the LED matrix, played in two NON-overlapping phases:

  Phase 1 — full-screen scrolling "<TEAM> HOME RUN!" banner in gold; pinwheel LEDs fire.
  Phase 2 — the normal live game screen (inning, count, outs, score) with a single
            base runner advancing 1B -> 2B -> 3B; pinwheel LEDs fire again.

Phase 2 reuses the live game renderer (renderers.games.game.render_live_game) and the
team banner so it matches the regular scoreboard exactly. The advancing runner is driven
through render_live_game's built-in home run base animation: it lights base index
(animation_time % 16) // 5, so passing animation_time = base_index * 5 lights one base
at a time.

This module is self-contained: call celebrate_homerun(matrix, config, scoreboard, team).
"""

import time

import debug
import pinwheel_leds
from driver import graphics
from renderers.games import game as gamerender
from renderers.games import teams

# Initialize pinwheel LED pins once (idempotent; no-op in mock mode off-Pi)
pinwheel_leds.setup()

# Phase 1 banner scroll speed — lower = faster
SCROLL_DELAY = 0.02

# Phase 1: how many times the banner scrolls across the screen
BANNER_PASSES = 2

# Phase 2: seconds each base stays lit as the runner advances
BASE_ADVANCE_HOLD = 1.0

# Phase 2 frame pacing
PHASE2_FRAME_DELAY = 0.03

# Gold/yellow — matches the base color; used for the banner text
HR_GOLD = (255, 200, 0)


def celebrate_homerun(matrix, config, scoreboard, team_name):
    """Run the full two-phase home run celebration on the matrix."""
    try:
        debug.log("Home run celebration starting for %s", team_name)
        _phase1_banner(matrix, config, team_name)
        _phase2_live_with_runner(matrix, config, scoreboard)
        debug.log("Home run celebration finished")
    except Exception as e:
        debug.error("Home run celebration error: %s", e)


def _phase1_banner(matrix, config, team_name):
    """Full-screen gold 'TEAM HOME RUN!' scrolled across BANNER_PASSES times; LEDs fire."""
    layout = config.layout
    font = layout.font("atbat.batter")
    text_color = graphics.Color(*HR_GOLD)

    text = f"  {team_name.upper()} HOME RUN!  "
    text_pixel_width = font["size"]["width"] * len(text)

    pinwheel_leds.trigger_async()

    offscreen = matrix.CreateFrameCanvas()
    for _ in range(BANNER_PASSES):
        x_pos = matrix.width
        # Scroll the banner until it has fully exited the left edge
        while x_pos > -text_pixel_width:
            offscreen.Clear()
            graphics.DrawText(offscreen, font["font"], x_pos, 10, text_color, text)
            x_pos -= 1
            offscreen = matrix.SwapOnVSync(offscreen)
            time.sleep(SCROLL_DELAY)


def _phase2_live_with_runner(matrix, config, scoreboard):
    """Normal live screen + a single runner advancing 1B -> 2B -> 3B; LEDs fire."""
    layout = config.layout
    colors = config.scoreboard_colors
    team_colors = config.team_colors

    pinwheel_leds.trigger_async()

    offscreen = matrix.CreateFrameCanvas()
    text_pos = offscreen.width

    for base_index in range(3):  # 0 -> 1B, 1 -> 2B, 2 -> 3B
        # animation_time = base_index * 5 makes render_live_game light exactly this base
        animation_time = base_index * 5
        hold_start = time.time()
        while time.time() - hold_start < BASE_ADVANCE_HOLD:
            offscreen.Clear()
            gamerender.render_live_game(
                offscreen, layout, colors, scoreboard, text_pos, animation_time, homerun_animation=True
            )
            teams.render_team_banner(
                offscreen,
                layout,
                team_colors,
                scoreboard.home_team,
                scoreboard.away_team,
                config.full_team_names,
                config.short_team_names_for_runs_hits,
                show_score=True,
            )
            offscreen = matrix.SwapOnVSync(offscreen)
            text_pos -= 1
            time.sleep(PHASE2_FRAME_DELAY)
