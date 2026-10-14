import math
import random

import pygame

from ..content import Effect, PowerUpSpec
from ..settings import HEIGHT, MUTED_TEXT_COLOR, PANEL_COLOR
from ..util import blit_centered, blit_centered_x, lighten, pulse


class PowerUpDrop:
    """A collectible falling from a destroyed enemy."""

    WIDTH = 30
    HEIGHT = 30

    def __init__(self, x, y, spec: PowerUpSpec):
        self.spec = spec
        self.base_x = x
        self.y = y
        self.vy = random.uniform(120, 200)
        self.bob_phase = random.uniform(0, math.tau)
        self.alive = True

    @property
    def x(self):
        return self.base_x + math.sin(self.bob_phase) * 30

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.WIDTH, self.HEIGHT)

    def update(self, dt):
        self.bob_phase += dt * 2
        self.y += self.vy * dt
        if self.y > HEIGHT + 20:
            self.alive = False

    def draw(self, surf, assets):
        r = self.rect
        color = lighten(self.spec.color, pulse(250) * 0.5)
        pygame.draw.rect(surf, PANEL_COLOR, r, border_radius=10)
        pygame.draw.rect(surf, color, r, width=2, border_radius=10)

        label = assets.tiny.render(self.spec.symbol, True, color)
        blit_centered(surf, label, r.center)

        name = assets.tiny.render(self.spec.name, True, MUTED_TEXT_COLOR)
        blit_centered_x(surf, name, r.centerx, r.bottom + 1)


class PowerUpEffect:
    """An active, timed buff on the player."""

    def __init__(self, spec: PowerUpSpec):
        self.effect = spec.effect
        self.timer = spec.timer
        self.symbol = spec.symbol
        self.color = spec.color
        self.active = True

    def refresh(self, spec: PowerUpSpec):
        self.timer = spec.timer

    def update(self, dt):
        self.timer -= dt
        if self.timer < 0:
            self.active = False

    def draw(self, surf, assets, x, y):
        img = assets.small.render(self.symbol, True, self.color)
        # blink during the last two seconds
        img.set_alpha(int(255 * pulse(50)) if self.timer < 2 else 255)
        surf.blit(img, (x, y))


def has_effect(effects, effect: Effect):
    return any(e.effect == effect for e in effects)
