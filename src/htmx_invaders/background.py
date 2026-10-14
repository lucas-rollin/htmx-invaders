"""Drifting angle-bracket / brace particles behind everything."""

import random

from .settings import BG_COLOR, GRID_COLOR, HEIGHT, WIDTH

GLYPHS = ("<", ">", "/", "{", "}", ";")


class _Particle:
    def __init__(self, assets):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.speed = random.uniform(10, 35)
        font = assets.font(random.randint(12, 22))
        # Rendered once; re-rendering text for every particle every frame is costly.
        self.image = font.render(random.choice(GLYPHS), True, GRID_COLOR)
        self.image.set_alpha(random.randint(20, 60))

    def update(self, dt):
        self.y += self.speed * dt
        if self.y > HEIGHT + 20:
            self.y = -20
            self.x = random.uniform(0, WIDTH)

    def draw(self, surf):
        surf.blit(self.image, (self.x, self.y))


class Background:
    def __init__(self, assets, count=100):
        self._particles = [_Particle(assets) for _ in range(count)]

    def update(self, dt):
        for p in self._particles:
            p.update(dt)

    def draw(self, surf):
        surf.fill(BG_COLOR)
        for p in self._particles:
            p.draw(surf)
