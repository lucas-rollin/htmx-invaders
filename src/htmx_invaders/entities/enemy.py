import math
import random

import pygame

from ..content import Framework
from ..settings import MUTED_TEXT_COLOR, PANEL_COLOR
from ..util import blit_centered, blit_centered_x


class Enemy:
    WIDTH = 52
    HEIGHT = 40

    def __init__(self, col, row, fw: Framework):
        self.col = col
        self.row = row
        self.fw = fw
        self.base_x = 0.0  # positioned by the Formation
        self.base_y = 0.0
        self.bob_phase = random.uniform(0, math.tau)
        self.alive = True

    @property
    def x(self):
        return self.base_x

    @property
    def y(self):
        return self.base_y + math.sin(self.bob_phase) * 3

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.WIDTH, self.HEIGHT)

    def update(self, dt):
        self.bob_phase += dt * 2

    def draw(self, surf, assets):
        r = self.rect
        pygame.draw.rect(surf, PANEL_COLOR, r, border_radius=10)
        pygame.draw.rect(surf, self.fw.color, r, width=2, border_radius=10)

        logo = assets.logo(self.fw)
        if logo:
            blit_centered(surf, logo, (r.centerx, r.centery - 2))

        name = assets.tiny.render(self.fw.name, True, MUTED_TEXT_COLOR)
        blit_centered_x(surf, name, r.centerx, r.bottom + 1)
