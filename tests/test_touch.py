import pygame

from htmx_invaders import touch
from htmx_invaders.settings import HEIGHT, WIDTH
from htmx_invaders.states import GameState
from htmx_invaders.touch import CombinedKeys, TouchControls, is_portrait_display

from .conftest import FakeAssets, Keys


def test_combined_keys():
    real = Keys({pygame.K_UP: True})
    virtual = {pygame.K_LEFT: True, pygame.K_RIGHT: False}
    combined = CombinedKeys(real, virtual)

    assert combined[pygame.K_UP] is True
    assert combined[pygame.K_LEFT] is True
    assert combined[pygame.K_RIGHT] is False
    assert combined[pygame.K_DOWN] is False


def test_is_mobile_device_detection(monkeypatch):
    assert touch.is_mobile_device() is False

    monkeypatch.setattr(touch, "IS_WASM", True)

    class FakeNav:
        userAgent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"

    class FakeWin:
        navigator = FakeNav()
        matchMedia = None

    class FakePlatform:
        window = FakeWin()

    import sys

    monkeypatch.setitem(sys.modules, "platform", FakePlatform)
    # Desktop user agent without coarse pointer
    assert touch.is_mobile_device() is False

    # Mobile user agent
    FakeNav.userAgent = "Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X)"
    assert touch.is_mobile_device() is True

    # Coarse pointer matchMedia
    FakeNav.userAgent = "Mozilla/5.0 (X11; Linux x86_64)"
    FakePlatform.window.matchMedia = lambda query: type(
        "MediaQueryList", (), {"matches": query == "(pointer: coarse)"}
    )()
    assert touch.is_mobile_device() is True


def test_portrait_display_detection(monkeypatch):
    assert is_portrait_display() is False

    monkeypatch.setattr(touch, "IS_WASM", True)
    monkeypatch.setattr(touch, "is_mobile_device", lambda: True)

    class FakeWin:
        innerWidth = 600
        innerHeight = 1000

    class FakePlatform:
        window = FakeWin()

    import sys

    monkeypatch.setitem(sys.modules, "platform", FakePlatform)
    assert is_portrait_display() is True

    FakeWin.innerWidth = 1200
    assert is_portrait_display() is False


def test_touch_handle_events():
    assets = FakeAssets()
    tc = TouchControls(assets)
    tc.enabled = False

    # Finger down
    ev_down = pygame.event.Event(pygame.FINGERDOWN, finger_id=1, x=0.5, y=0.5)
    tc.handle_event(ev_down)
    assert tc.enabled is True
    assert 1 in tc.active_touches
    assert tc.active_touches[1] == (WIDTH * 0.5, HEIGHT * 0.5)
    assert len(tc.tap_events) == 1

    # Finger motion
    ev_motion = pygame.event.Event(pygame.FINGERMOTION, finger_id=1, x=0.6, y=0.7)
    tc.handle_event(ev_motion)
    assert tc.active_touches[1] == (WIDTH * 0.6, HEIGHT * 0.7)

    # Finger up
    ev_up = pygame.event.Event(pygame.FINGERUP, finger_id=1)
    tc.handle_event(ev_up)
    assert 1 not in tc.active_touches


def test_mouse_events_fallback():
    assets = FakeAssets()
    tc = TouchControls(assets)

    tc.handle_event(
        pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1, pos=(200, 300))
    )
    assert tc.mouse_pos == (200.0, 300.0)

    tc.handle_event(pygame.event.Event(pygame.MOUSEMOTION, pos=(250, 350)))
    assert tc.mouse_pos == (250.0, 350.0)

    tc.handle_event(pygame.event.Event(pygame.MOUSEBUTTONUP, button=1))
    assert tc.mouse_pos is None


def test_menu_state_tap_starts_game():
    assets = FakeAssets()
    tc = TouchControls(assets)
    tc.tap_events.append((WIDTH / 2, HEIGHT / 2))

    just_pressed = set()
    keys = tc.update_inputs(Keys(), just_pressed, GameState.MENU)

    assert pygame.K_SPACE in just_pressed
    assert keys[pygame.K_SPACE] is False


def test_playing_state_movement_and_shoot():
    assets = FakeAssets()
    tc = TouchControls(assets)

    # Left button touch
    lx, ly = tc.left_rect.center
    tc.active_touches[0] = (float(lx), float(ly))
    just_pressed = set()
    keys = tc.update_inputs(Keys(), just_pressed, GameState.PLAYING)

    assert keys[pygame.K_LEFT] is True
    assert keys[pygame.K_RIGHT] is False

    # Right button touch
    rx, ry = tc.right_rect.center
    tc.active_touches[0] = (float(rx), float(ry))
    just_pressed = set()
    keys = tc.update_inputs(Keys(), just_pressed, GameState.PLAYING)

    assert keys[pygame.K_LEFT] is False
    assert keys[pygame.K_RIGHT] is True

    # Shoot button touch
    sx, sy = tc.shoot_rect.center
    tc.active_touches[0] = (float(sx), float(sy))
    tc.tap_events.append((float(sx), float(sy)))
    just_pressed = set()
    keys = tc.update_inputs(Keys(), just_pressed, GameState.PLAYING)

    assert keys[pygame.K_SPACE] is True
    assert pygame.K_SPACE in just_pressed


def test_menu_button_triggers_escape_across_states():
    assets = FakeAssets()
    tc = TouchControls(assets)
    mx, my = tc.menu_rect.center

    for st in (GameState.PLAYING, GameState.GAME_OVER, GameState.WAVE_CLEAR):
        tc.tap_events.append((float(mx), float(my)))
        just_pressed = set()
        tc.update_inputs(Keys(), just_pressed, st)
        assert pygame.K_ESCAPE in just_pressed


def test_game_over_tap_retries():
    assets = FakeAssets()
    tc = TouchControls(assets)
    tc.tap_events.append((100.0, 100.0))  # not menu button

    just_pressed = set()
    tc.update_inputs(Keys(), just_pressed, GameState.GAME_OVER)
    assert pygame.K_r in just_pressed


def test_touch_draw_renders_all_states(monkeypatch):
    surf = pygame.Surface((WIDTH, HEIGHT))
    assets = FakeAssets()
    tc = TouchControls(assets)
    tc.enabled = True

    for st in (
        GameState.MENU,
        GameState.PLAYING,
        GameState.WAVE_CLEAR,
        GameState.GAME_OVER,
    ):
        tc.draw(surf, st)

    # Portrait warning branch
    monkeypatch.setattr(touch, "is_portrait_display", lambda: True)
    tc.draw(surf, GameState.PLAYING)
