"""Runs the real main loop for a few seconds.

Needs the actual files in ./assets, so it's skipped when run from elsewhere.
"""

import asyncio
import os

import pygame
import pytest

from htmx_invaders import main as game_main
from htmx_invaders.paths import FONT_PATH

pytestmark = pytest.mark.skipif(
    not os.path.exists(FONT_PATH),
    reason="run pytest from the repo root (needs ./assets)",
)


def test_main_loop_runs_a_playthrough(monkeypatch):
    frame = {"n": 0}

    def fake_events():
        frame["n"] += 1
        n = frame["n"]
        if n == 3 or (5 < n < 400 and n % 7 == 0):
            return [
                pygame.event.Event(pygame.KEYDOWN, key=pygame.K_SPACE)
            ]  # start, then shoot
        if n == 400:
            return [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)]
        return []

    monkeypatch.setattr(pygame.event, "get", fake_events)
    asyncio.run(game_main.main())
    assert frame["n"] == 400
