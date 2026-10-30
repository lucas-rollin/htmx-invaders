import random

import pygame

from ..content import Effect
from ..settings import (
    DANGER_COLOR,
    HEIGHT,
    HTMX_COLOR,
    HTMX_GLOW,
    HTMX_MARK_COLOR,
    MAX_LIVES,
    WIDTH,
)
from ..util import blit_centered, pulse, render_rich_text
from .bullet import Bullet
from .powerup import has_effect


class Player:
    WIDTH = 71
    HEIGHT = 36
    SPEED = 360
    COOLDOWN = 0.28
    BULLET_SPEED = 560
    SPREAD_SPEED = 150
    HIT_IMMUNITY = 1.5

    def __init__(self):
        self.x = WIDTH / 2 - self.WIDTH / 2
        self.y = HEIGHT - 70
        self.cooldown_left = 0.0
        self.lives = MAX_LIVES
        self.hit_flash = 0.0
        self.immunity = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.WIDTH, self.HEIGHT)

    def update(self, dt, keys):
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        self.x += dx * self.SPEED * dt
        self.x = max(10, min(WIDTH - self.WIDTH - 10, self.x))

        self.cooldown_left = max(0.0, self.cooldown_left - dt)
        self.hit_flash = max(0.0, self.hit_flash - dt)
        self.immunity = max(0.0, self.immunity - dt)

    def take_hit(self, fatal=False):
        self.lives = 0 if fatal else self.lives - 1
        self.hit_flash = 0.3
        self.immunity = self.HIT_IMMUNITY

    def try_shoot(self, effects):
        """Return the bullets fired (empty list while on cooldown)."""
        if self.cooldown_left > 0:
            return []

        cooldown = (
            self.COOLDOWN / 2
            if has_effect(effects, Effect.RAPID_FIRE)
            else self.COOLDOWN
        )
        self.cooldown_left = cooldown

        pierce = has_effect(effects, Effect.PIERCE_SHOT)
        cx = self.x + self.WIDTH / 2
        spreads = (
            (0, self.SPREAD_SPEED, -self.SPREAD_SPEED)
            if has_effect(effects, Effect.TRIPLE_SHOT)
            else (0,)
        )
        return [
            Bullet(cx, self.y - 6, -self.BULLET_SPEED, vx, HTMX_COLOR, pierce)
            for vx in spreads
        ]

    def draw(self, surf, assets, effects=()):
        r = self.rect
        color = DANGER_COLOR if self.hit_flash > 0 else HTMX_COLOR
        hull = (28, 28, 40)

        shield = next((e for e in effects if e.effect == Effect.SHIELD), None)
        if shield:
            alpha = int(70 * pulse(50)) if shield.timer < 2 else 40
            glow = pygame.Surface((r.width + 24, r.height + 24), pygame.SRCALPHA)
            pygame.draw.rect(
                glow, (*HTMX_GLOW, alpha), glow.get_rect(), border_radius=14
            )
            surf.blit(glow, (r.x - 12, r.y - 12))

        def mx(x):
            """Mirror an x coordinate across the sprite's vertical axis."""
            return r.left + r.right - 1 - x

        # Lateral wings
        wing = [
            (r.left + 8, r.top + 8),
            (r.left - 7, r.bottom - 2),
            (r.left + 8, r.bottom - 4),
        ]
        for pts in (wing, [(mx(x), y) for x, y in wing]):
            pygame.draw.polygon(surf, hull, pts)
            pygame.draw.polygon(surf, color, pts, width=2)

        # Nose
        cx = r.centerx
        tip = (cx, r.top - 7)
        left_base = (cx - 9, r.top + 2)
        right_base = (cx + 9, r.top + 2)
        pygame.draw.polygon(surf, hull, [tip, left_base, right_base])
        pygame.draw.line(surf, color, tip, left_base, 2)
        pygame.draw.line(surf, color, tip, right_base, 2)

        # Body
        pygame.draw.rect(surf, hull, r, border_radius=8)
        pygame.draw.rect(surf, color, r, width=2, border_radius=8)

        logo = render_rich_text(
            assets.med,
            [
                ("<", HTMX_MARK_COLOR),
                ("/", color),
                (">", HTMX_MARK_COLOR),
            ],
        )
        blit_centered(surf, logo, r.center)

        # engine flicker
        flame_h = random.randint(4, 10)
        pygame.draw.polygon(
            surf,
            (255, 200, 90),
            [
                (r.centerx - 6, r.bottom),
                (r.centerx + 6, r.bottom),
                (r.centerx, r.bottom + flame_h),
            ],
        )
