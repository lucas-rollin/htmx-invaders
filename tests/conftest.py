"""Shared fixtures. Tests run headless and never touch real assets."""

import os

# Must be set before pygame is imported anywhere.
os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")

import pygame
import pytest

from htmx_invaders.content import POWERUPS, Effect
from htmx_invaders.entities import PowerUpEffect
from htmx_invaders.game import Game


@pytest.fixture(scope="session", autouse=True)
def _pygame():
    pygame.display.init()
    pygame.font.init()
    yield
    pygame.quit()


class Keys(dict):
    """Stand-in for pygame.key.get_pressed(): unset keys read as False."""

    def __missing__(self, key):
        return False


class FakeAudio:
    """Records what the game asked to play instead of making noise."""

    def __init__(self):
        self.played = []
        self.music = []

    def play(self, name):
        self.played.append(name)

    def play_menu_music(self):
        self.music.append("menu")

    def play_random_soundtrack(self):
        self.music.append("soundtrack")


class FakeAssets:
    """Fonts from pygame's built-in default; no logo files needed."""

    def __init__(self):
        self.big = pygame.font.Font(None, 56)
        self.med = pygame.font.Font(None, 28)
        self.small = pygame.font.Font(None, 18)
        self.tiny = pygame.font.Font(None, 14)

    def font(self, size, bold=False):
        return pygame.font.Font(None, size)

    def logo(self, fw):
        return None


def spec_for(effect: Effect):
    return next(p for p in POWERUPS if p.effect == effect)


def effect_for(effect: Effect):
    return PowerUpEffect(spec_for(effect))


@pytest.fixture
def keys():
    return Keys()


@pytest.fixture
def audio():
    return FakeAudio()


@pytest.fixture
def assets():
    return FakeAssets()


@pytest.fixture
def game(assets, audio):
    return Game(assets, audio)


@pytest.fixture
def playing(game):
    """A game in PLAYING state with deterministic, quiet enemies."""
    game.reset()
    game.enemy_shoot_timer = 1e9  # no random enemy fire during tests
    return game
