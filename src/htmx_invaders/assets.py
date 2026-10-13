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
