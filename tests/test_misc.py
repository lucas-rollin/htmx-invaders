import pygame

from htmx_invaders import main, screens
from htmx_invaders.content import FRAMEWORKS, JOKES, POWERUPS
from htmx_invaders.util import lighten, pulse

from .conftest import FakeAssets


def test_content_is_consistent():
    assert len({f.name for f in FRAMEWORKS}) == len(FRAMEWORKS)
    assert all(f.file.endswith(".png") for f in FRAMEWORKS)
    assert len({p.effect for p in POWERUPS}) == len(POWERUPS)
    assert all(p.weight > 0 for p in POWERUPS)
    assert JOKES


def test_lighten_bounds():
    assert lighten((10, 20, 30), 0) == (10, 20, 30)
    assert lighten((10, 20, 30), 1) == (255, 255, 255)


def test_pulse_in_unit_range():
    assert 0 <= pulse(250) <= 1


def test_poll_events_escape_desktop(monkeypatch):
    monkeypatch.setattr(main, "IS_WASM", False)
    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    )
    running, pressed = main.poll_events()
    assert running is False
    assert pygame.K_ESCAPE in pressed


def test_poll_events_escape_wasm(monkeypatch):
    monkeypatch.setattr(main, "IS_WASM", True)
    monkeypatch.setattr(
        pygame.event,
        "get",
        lambda: [pygame.event.Event(pygame.KEYDOWN, key=pygame.K_ESCAPE)],
    )
    running, pressed = main.poll_events()
    assert running is True
    assert pygame.K_ESCAPE in pressed


def test_game_over_screen_renders_without_crash(monkeypatch):
    surf = pygame.Surface((1280, 720))
    assets = FakeAssets()

    # Desktop native
    monkeypatch.setattr(screens, "IS_WASM", False)
    monkeypatch.setattr(screens, "is_mobile_device", lambda: False)
    screens.draw_game_over(surf, assets, 100)
    screens.draw_menu(surf, assets)

    # Desktop Web (WASM but not mobile)
    monkeypatch.setattr(screens, "IS_WASM", True)
    monkeypatch.setattr(screens, "is_mobile_device", lambda: False)
    screens.draw_game_over(surf, assets, 100)
    screens.draw_menu(surf, assets)

    # Mobile Web
    monkeypatch.setattr(screens, "is_mobile_device", lambda: True)
    screens.draw_game_over(surf, assets, 100)
    screens.draw_menu(surf, assets)


def test_hud_renders_without_crash():
    surf = pygame.Surface((1280, 720))
    assets = FakeAssets()
    from htmx_invaders.content import Effect

    from .conftest import effect_for

    effects = [effect_for(Effect.SHIELD), effect_for(Effect.TRIPLE_SHOT)]
    screens.draw_hud(surf, assets, score=1240, level=3, effects=effects, lives=3)
