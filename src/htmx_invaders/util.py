"""Small drawing helpers shared across modules."""

import math

import pygame


def pulse(period_ms):
    """Smooth 0..1 oscillation driven by the wall clock."""
    return (math.sin(pygame.time.get_ticks() / period_ms) + 1) / 2


def lighten(color, t):
    """Blend `color` toward white by `t` (0..1)."""
    return tuple(int(c + (255 - c) * t) for c in color)


def blit_centered(surf, img, center):
    surf.blit(img, img.get_rect(center=(int(center[0]), int(center[1]))))


def blit_centered_x(surf, img, cx, y):
    surf.blit(img, (cx - img.get_width() / 2, y))


def render_rich_text(font, segments, antialias=True):
    """Render [(text, color), ...] into a single surface."""
    rendered = [font.render(text, antialias, color) for text, color in segments]

    width = sum(s.get_width() for s in rendered)
    height = max(s.get_height() for s in rendered)

    surface = pygame.Surface((width, height), pygame.SRCALPHA)

    x = 0
    for segment in rendered:
        surface.blit(segment, (x, (height - segment.get_height()) // 2))
        x += segment.get_width()

    return surface
