"""Stateless drawing for the HUD, menu and overlays."""

import pygame

from .content import FRAMEWORKS
from .settings import (
    DANGER_COLOR,
    HEIGHT,
    HTMX_COLOR,
    IS_WASM,
    PANEL_COLOR,
    TEXT_COLOR,
    WIDTH,
)
from .touch import is_mobile_device
from .util import blit_centered, blit_centered_x, lighten, pulse


def _dim(surf, alpha):
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((10, 10, 16, alpha))
    surf.blit(overlay, (0, 0))


def draw_hud(surf, assets, score, level, effects, lives):
    surf.blit(assets.small.render(f"SCORE {score}", True, TEXT_COLOR), (68, 14))

    surf.blit(assets.small.render("LIVES", True, TEXT_COLOR), (240, 14))
    tag = assets.small.render("</>", True, HTMX_COLOR)
    for i in range(lives):
        surf.blit(tag, (305 + i * 32, 12))

    wave = assets.small.render(f"WAVE {level}", True, TEXT_COLOR)
    blit_centered_x(surf, wave, WIDTH / 2, 14)

    surf.blit(assets.small.render("POWERUPS", True, TEXT_COLOR), (880, 14))
    x = 980
    for e in effects:
        e.draw(surf, assets, x, 14)
        x += assets.small.size(e.symbol)[0] + 8


def draw_wave_clear(surf, assets, text, color):
    _dim(surf, 120)
    blit_centered_x(
        surf, assets.big.render(text, True, color), WIDTH / 2, HEIGHT / 2 - 60
    )
    sub = assets.small.render("next wave incoming...", True, TEXT_COLOR)
    blit_centered_x(surf, sub, WIDTH / 2, HEIGHT / 2 + 10)


def draw_game_over(surf, assets, score):
    _dim(surf, 170)
    title = assets.big.render("FATIGUE WON THIS TIME", True, DANGER_COLOR)
    blit_centered_x(surf, title, WIDTH / 2, HEIGHT / 2 - 90)
    final = assets.med.render(f"final score: {score}", True, TEXT_COLOR)
    blit_centered_x(surf, final, WIDTH / 2, HEIGHT / 2 - 20)
    if is_mobile_device():
        hint_text = "tap screen or press R to retry  -  ESC for menu"
    elif IS_WASM:
        hint_text = "press R to retry  -  ESC for menu"
    else:
        hint_text = "press R to retry  -  ESC to quit"
    hint = assets.small.render(hint_text, True, TEXT_COLOR)
    blit_centered_x(surf, hint, WIDTH / 2, HEIGHT / 2 + 30)


def draw_menu(surf, assets):
    title = assets.big.render("</> vs The JS Fatigue", True, HTMX_COLOR)
    blit_centered_x(surf, title, WIDTH / 2, 130)

    sub = assets.small.render(
        "defend the simple web. shoot the fatigue before it lands.", True, TEXT_COLOR
    )
    blit_centered_x(surf, sub, WIDTH / 2, 200)

    # preview row of enemies
    spacing = 70
    start_x = WIDTH / 2 - (len(FRAMEWORKS) * spacing) / 2 + spacing / 2
    for i, fw in enumerate(FRAMEWORKS):
        r = pygame.Rect(int(start_x + i * spacing - 24), 270, 48, 36)
        pygame.draw.rect(surf, PANEL_COLOR, r, border_radius=8)
        pygame.draw.rect(surf, fw.color, r, width=2, border_radius=8)
        logo = assets.logo(fw)
        if logo:
            blit_centered(surf, logo, r.center)

    controls_text = (
        ("TOUCH CONTROLS / ARROWS  -  move", "TAP / SPACE  -  shoot")
        if is_mobile_device()
        else ("ARROWS / A D  -  move", "SPACE  -  shoot")
    )
    for i, line in enumerate(controls_text):
        blit_centered_x(
            surf, assets.small.render(line, True, TEXT_COLOR), WIDTH / 2, 360 + i * 28
        )

    color = lighten(HTMX_COLOR, pulse(250) * 0.5)
    start_msg = (
        "TAP SCREEN OR PRESS SPACE TO START"
        if is_mobile_device()
        else "PRESS SPACE TO START"
    )
    start = assets.med.render(start_msg, True, color)
    blit_centered_x(surf, start, WIDTH / 2, 440)
