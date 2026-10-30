"""Generate web, PWA, and desktop icon assets from the player sprite."""

import os
import random
import sys
from pathlib import Path

# Ensure project root and src/ are in sys.path regardless of execution directory
REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "src"))
os.chdir(REPO_ROOT)

os.environ["SDL_VIDEODRIVER"] = "dummy"  # no window needed
os.environ["SDL_AUDIODRIVER"] = "dummy"

import pygame

pygame.init()
pygame.display.set_mode((1, 1))  # needed for convert_alpha / fonts on some setups

from htmx_invaders.assets import Assets
from htmx_invaders.entities.player import Player
from htmx_invaders.settings import BG_COLOR

# Standard sizes for icons (PWA, Android, iOS, Favicons, Desktop)
SIZES = [512, 192, 180, 96, 64, 48, 32, 16]

ICONS_DIR = REPO_ROOT / "icons"
WEB_DIR = REPO_ROOT / "web"


def render_player_sprite(assets: Assets) -> pygame.Surface:
    """Render the player ship at native size on a transparent surface."""
    random.seed(3)  # freezes the engine flame height (randint 4..10)
    canvas = pygame.Surface((128, 128), pygame.SRCALPHA)
    p = Player()
    p.x = (128 - p.WIDTH) / 2
    p.y = 30
    p.draw(canvas, assets)

    # Trim transparent margins so scaling is predictable
    bbox = canvas.get_bounding_rect()
    return canvas.subsurface(bbox).copy()


def make_icon(
    sprite: pygame.Surface, size: int, bg=None, fill: float = 0.7
) -> pygame.Surface:
    """Square icon with the sprite centered, `fill` = fraction of width/height used."""
    icon = pygame.Surface((size, size), pygame.SRCALPHA)
    if bg is not None:
        icon.fill(bg)
    max_dim = max(sprite.get_width(), sprite.get_height())
    scale = size * fill / max_dim
    w = max(1, round(sprite.get_width() * scale))
    h = max(1, round(sprite.get_height() * scale))
    scaled = pygame.transform.smoothscale(sprite, (w, h))
    icon.blit(scaled, ((size - w) // 2, (size - h) // 2))
    return icon


def main():
    assets = Assets()
    sprite = render_player_sprite(assets)

    ICONS_DIR.mkdir(parents=True, exist_ok=True)
    WEB_DIR.mkdir(parents=True, exist_ok=True)

    # Save native resolution sprite in icons/
    pygame.image.save(sprite, str(ICONS_DIR / "player_native.png"))

    # Generate standard square icons for reference/archive (gitignored)
    icons_by_size = {}
    for s in SIZES:
        icon = make_icon(sprite, s, bg=BG_COLOR, fill=0.7)
        icons_by_size[s] = icon
        pygame.image.save(icon, str(ICONS_DIR / f"icon-{s}.png"))

    # Maskable icons (55% fill to stay inside Android circular safe zone)
    maskable_512 = make_icon(sprite, 512, bg=BG_COLOR, fill=0.55)
    pygame.image.save(maskable_512, str(ICONS_DIR / "icon-maskable-512.png"))

    # Apple touch icon (180x180)
    apple_touch = make_icon(sprite, 180, bg=BG_COLOR, fill=0.7)
    pygame.image.save(apple_touch, str(ICONS_DIR / "apple-touch-icon.png"))

    # Favicons (transparent background, 95% fill to maximize visibility at small sizes)
    favicon_96 = make_icon(sprite, 96, bg=None, fill=0.95)
    favicon_32 = make_icon(sprite, 32, bg=None, fill=0.95)
    pygame.image.save(favicon_96, str(ICONS_DIR / "favicon.png"))
    pygame.image.save(favicon_32, str(ICONS_DIR / "favicon.ico"))

    # Emit only the 6 required web & PWA icons directly into web/
    web_icons = {
        "favicon.png": favicon_96,
        "favicon.ico": favicon_32,
        "apple-touch-icon.png": apple_touch,
        "icon-192.png": icons_by_size[192],
        "icon-512.png": icons_by_size[512],
        "icon-maskable-512.png": maskable_512,
    }

    for filename, surf in web_icons.items():
        pygame.image.save(surf, str(WEB_DIR / filename))

    print(f"Generated icons in {ICONS_DIR.relative_to(REPO_ROOT)} and {WEB_DIR.relative_to(REPO_ROOT)} (6 web icons)")


if __name__ == "__main__":
    main()
