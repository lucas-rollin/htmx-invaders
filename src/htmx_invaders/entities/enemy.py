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
        self._rect = pygame.Rect(0, 0, self.WIDTH, self.HEIGHT)

    @property
    def x(self):
        return self.base_x

    @property
    def y(self):
        return self.base_y + math.sin(self.bob_phase) * 3

    @property
    def rect(self):
        self._rect.x = int(self.x)
        self._rect.y = int(self.y)
        return self._rect

    def update(self, dt):
        self.bob_phase += dt * 2

    def draw(self, surf, assets):
        sprite_info = getattr(assets, "enemy_sprite", None)
        if sprite_info:
            res = sprite_info(self.fw)
            if res:
                card_surf, offset_x = res
                surf.blit(card_surf, (int(self.x) - offset_x, int(self.y)))
                return

        r = self.rect
        pygame.draw.rect(surf, PANEL_COLOR, r, border_radius=10)
        pygame.draw.rect(surf, self.fw.color, r, width=2, border_radius=10)

        logo = getattr(assets, "logo", lambda _: None)(self.fw)
        if logo:
            blit_centered(surf, logo, (r.centerx, r.centery - 2))

        name = assets.tiny.render(self.fw.name, True, MUTED_TEXT_COLOR)
        blit_centered_x(surf, name, r.centerx, r.bottom + 1)
