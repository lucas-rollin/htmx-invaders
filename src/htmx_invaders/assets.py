"""Visual assets (fonts and enemy logos). Create after the display exists."""

import os

import pygame

from .content import FRAMEWORKS, Framework
from .paths import FONT_PATH, IMG_DIR
from .settings import LOGO_SIZE


class Assets:
    def __init__(self):
        self._fonts = {}
        self.big = self.font(56, bold=True)
        self.med = self.font(28, bold=True)
        self.small = self.font(18)
        self.tiny = self.font(14)
        self._logos = self._load_logos()
        self._enemy_sprites = self._prebuild_enemy_sprites()

    def font(self, size, bold=False):
        key = (size, bold)
        if key not in self._fonts:
            f = pygame.font.Font(FONT_PATH, size)
            f.set_bold(bold)
            self._fonts[key] = f
        return self._fonts[key]

    def logo(self, fw: Framework):
        """Scaled logo surface, or None if it failed to load."""
        return self._logos.get(fw.name)

    def enemy_sprite(self, fw: Framework):
        """Pre-rendered (surface, offset_x) tuple for the framework card."""
        return self._enemy_sprites.get(fw.name)

    def _prebuild_enemy_sprites(self):
        from .entities.enemy import Enemy
        from .settings import MUTED_TEXT_COLOR, PANEL_COLOR
        from .util import blit_centered, blit_centered_x

        sprites = {}
        for fw in FRAMEWORKS:
            name_surf = self.tiny.render(fw.name, True, MUTED_TEXT_COLOR)
            name_w = name_surf.get_width()
            offset_x = max(0, (name_w - Enemy.WIDTH + 1) // 2)
            total_w = Enemy.WIDTH + 2 * offset_x
            total_h = Enemy.HEIGHT + 1 + name_surf.get_height()
            surf = pygame.Surface((total_w, total_h), pygame.SRCALPHA)

            r_card = pygame.Rect(offset_x, 0, Enemy.WIDTH, Enemy.HEIGHT)
            pygame.draw.rect(surf, PANEL_COLOR, r_card, border_radius=10)
            pygame.draw.rect(surf, fw.color, r_card, width=2, border_radius=10)
            logo = self.logo(fw)
            if logo:
                blit_centered(surf, logo, (r_card.centerx, r_card.centery - 2))
            blit_centered_x(surf, name_surf, r_card.centerx, r_card.bottom + 1)

            sprites[fw.name] = (surf, offset_x)
        return sprites

    @staticmethod
    def _load_logos():
        logos = {}
        for fw in FRAMEWORKS:
            path = os.path.join(IMG_DIR, fw.file)
            try:
                img = pygame.image.load(path).convert_alpha()
            except (pygame.error, OSError) as e:
                print(f"[htmx_invaders] couldn't load {path}: {e}")
                continue
            w, h = img.get_size()
            scale = LOGO_SIZE / max(w, h)
            size = (max(1, round(w * scale)), max(1, round(h * scale)))
            logos[fw.name] = pygame.transform.smoothscale(img, size)
        return logos
