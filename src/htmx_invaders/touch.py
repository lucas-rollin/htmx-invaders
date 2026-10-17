"""Mobile virtual controls and touch handling."""

import pygame

from .settings import (
    HEIGHT,
    HTMX_COLOR,
    HTMX_GLOW,
    IS_WASM,
    MUTED_TEXT_COLOR,
    PANEL_COLOR,
    TEXT_COLOR,
    WIDTH,
)
from .states import GameState
from .util import blit_centered_x


class CombinedKeys:
    """Combines real pygame keys with synthetic virtual button states."""

    def __init__(self, physical_keys, virtual_keys):
        self._physical = physical_keys
        self._virtual = virtual_keys

    def __getitem__(self, key):
        return bool(self._virtual.get(key, False) or self._physical[key])


def is_mobile_device() -> bool:
    """Return True if running on a mobile browser or primary touch device."""
    if IS_WASM:
        try:
            import platform  # type: ignore[import-not-found]

            win = platform.window
            nav = getattr(win, "navigator", None)
            if nav:
                ua = str(getattr(nav, "userAgent", "")).lower()
                mobile_keywords = (
                    "mobile",
                    "android",
                    "iphone",
                    "ipad",
                    "ipod",
                    "windows phone",
                )
                if any(k in ua for k in mobile_keywords):
                    return True

            match_media = getattr(win, "matchMedia", None)
            if match_media and match_media("(pointer: coarse)").matches:
                return True
        except (AttributeError, ImportError, TypeError, OSError):
            pass
    return False


def is_portrait_display() -> bool:
    """Return True if running on a mobile device held in portrait mode."""
    if IS_WASM and is_mobile_device():
        try:
            import platform  # type: ignore[import-not-found]

            win = platform.window
            if hasattr(win, "innerWidth") and hasattr(win, "innerHeight"):
                return bool(win.innerWidth < win.innerHeight)
        except (AttributeError, ImportError, TypeError, OSError):
            pass
    return False


class TouchControls:
    def __init__(self, assets):
        self.assets = assets
        self.enabled = is_mobile_device()
        self.active_touches: dict[int, tuple[float, float]] = {}
        self.mouse_pos: tuple[float, float] | None = None
        self.tap_events: list[tuple[float, float]] = []

        # Virtual buttons layout (1280 x 720)
        self.left_rect = pygame.Rect(35, 590, 100, 95)
        self.left_hitbox = pygame.Rect(10, 550, 135, 160)

        self.right_rect = pygame.Rect(150, 590, 100, 95)
        self.right_hitbox = pygame.Rect(145, 550, 135, 160)

        self.shoot_rect = pygame.Rect(1125, 585, 120, 105)
        self.shoot_hitbox = pygame.Rect(1070, 540, 200, 170)

        self.menu_rect = pygame.Rect(1175, 12, 85, 38)
        self.menu_hitbox = pygame.Rect(1155, 6, 115, 55)

        self.is_left_held = False
        self.is_right_held = False
        self.is_shoot_held = False

    def handle_event(self, event: pygame.event.Event):
        """Process touch and pointer events."""
        if event.type == pygame.FINGERDOWN:
            self.enabled = True
            pos = (event.x * WIDTH, event.y * HEIGHT)
            self.active_touches[event.finger_id] = pos
            self.tap_events.append(pos)
        elif event.type == pygame.FINGERMOTION:
            pos = (event.x * WIDTH, event.y * HEIGHT)
            self.active_touches[event.finger_id] = pos
        elif event.type == pygame.FINGERUP:
            self.active_touches.pop(event.finger_id, None)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if not self.active_touches:
                self.mouse_pos = (float(event.pos[0]), float(event.pos[1]))
                self.tap_events.append(self.mouse_pos)
        elif event.type == pygame.MOUSEMOTION:
            if self.mouse_pos is not None:
                self.mouse_pos = (float(event.pos[0]), float(event.pos[1]))
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.mouse_pos = None

    def update_inputs(self, raw_keys, just_pressed: set[int], state: GameState):
        """Update virtual button states and synthesize keys / just_pressed events."""
        pointers = list(self.active_touches.values())
        if self.mouse_pos is not None:
            pointers.append(self.mouse_pos)

        # Check button hold states
        self.is_left_held = any(self.left_hitbox.collidepoint(p) for p in pointers)
        self.is_right_held = any(self.right_hitbox.collidepoint(p) for p in pointers)
        self.is_shoot_held = any(self.shoot_hitbox.collidepoint(p) for p in pointers)

        # Process tap events
        taps = self.tap_events
        self.tap_events = []

        for tap in taps:
            if self.menu_hitbox.collidepoint(tap):
                just_pressed.add(pygame.K_ESCAPE)
                continue

            if state is GameState.MENU:
                just_pressed.add(pygame.K_SPACE)
            elif state is GameState.GAME_OVER:
                just_pressed.add(pygame.K_r)
            elif state is GameState.PLAYING and self.shoot_hitbox.collidepoint(tap):
                just_pressed.add(pygame.K_SPACE)

        # In playing state, holding shoot continuously adds K_SPACE (respects weapon cooldown)
        if state is GameState.PLAYING and self.is_shoot_held:
            just_pressed.add(pygame.K_SPACE)

        virtual_keys = {
            pygame.K_LEFT: self.is_left_held,
            pygame.K_RIGHT: self.is_right_held,
            pygame.K_SPACE: self.is_shoot_held,
        }
        return CombinedKeys(raw_keys, virtual_keys)

    def draw(self, surf: pygame.Surface, state: GameState):
        """Draw virtual controls and orientation warning if needed."""
        if is_portrait_display():
            self._draw_orientation_warning(surf)
            return

        if not self.enabled:
            return

        # Always draw Menu button if not on MENU
        if state is not GameState.MENU:
            self._draw_button(
                surf,
                self.menu_rect,
                label="MENU",
                font=self.assets.small,
                active=any(
                    self.menu_hitbox.collidepoint(p) for p in self._get_pointers()
                ),
            )

        # Draw gameplay buttons during PLAYING and WAVE_CLEAR
        if state in (GameState.PLAYING, GameState.WAVE_CLEAR):
            self._draw_button(
                surf,
                self.left_rect,
                icon="left",
                active=self.is_left_held,
            )
            self._draw_button(
                surf,
                self.right_rect,
                icon="right",
                active=self.is_right_held,
            )
            self._draw_button(
                surf,
                self.shoot_rect,
                label="</>",
                sublabel="FIRE",
                font=self.assets.med,
                active=self.is_shoot_held,
            )

    def _get_pointers(self):
        pointers = list(self.active_touches.values())
        if self.mouse_pos is not None:
            pointers.append(self.mouse_pos)
        return pointers

    def _draw_button(
        self,
        surf: pygame.Surface,
        rect: pygame.Rect,
        label: str | None = None,
        sublabel: str | None = None,
        icon: str | None = None,
        font: pygame.font.Font | None = None,
        active: bool = False,
    ):
        btn_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg = (59, 130, 246, 170) if active else (24, 24, 38, 120)
        border = (147, 197, 253, 240) if active else (59, 130, 246, 140)
        border_width = 3 if active else 2

        pygame.draw.rect(
            btn_surf, bg, (0, 0, rect.width, rect.height), border_radius=16
        )
        pygame.draw.rect(
            btn_surf,
            border,
            (0, 0, rect.width, rect.height),
            width=border_width,
            border_radius=16,
        )

        if icon == "left":
            cx, cy = rect.width // 2, rect.height // 2
            pts = [(cx + 14, cy - 18), (cx + 14, cy + 18), (cx - 14, cy)]
            c = (255, 255, 255, 255) if active else (220, 220, 235, 200)
            pygame.draw.polygon(btn_surf, c, pts)
        elif icon == "right":
            cx, cy = rect.width // 2, rect.height // 2
            pts = [(cx - 14, cy - 18), (cx - 14, cy + 18), (cx + 14, cy)]
            c = (255, 255, 255, 255) if active else (220, 220, 235, 200)
            pygame.draw.polygon(btn_surf, c, pts)
        elif label and font:
            c = (255, 255, 255) if active else (220, 220, 235)
            text_surf = font.render(label, True, c)
            if sublabel:
                btn_surf.blit(
                    text_surf,
                    (
                        rect.width // 2 - text_surf.get_width() // 2,
                        rect.height // 2 - text_surf.get_height() + 2,
                    ),
                )
                sc = (147, 197, 253) if active else (150, 150, 165)
                sub_surf = self.assets.tiny.render(sublabel, True, sc)
                btn_surf.blit(
                    sub_surf,
                    (rect.width // 2 - sub_surf.get_width() // 2, rect.height // 2 + 8),
                )
            else:
                btn_surf.blit(
                    text_surf,
                    (
                        rect.width // 2 - text_surf.get_width() // 2,
                        rect.height // 2 - text_surf.get_height() // 2,
                    ),
                )

        surf.blit(btn_surf, (rect.x, rect.y))

    def _draw_orientation_warning(self, surf: pygame.Surface):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 16, 230))
        surf.blit(overlay, (0, 0))

        box_w, box_h = 600, 240
        box_rect = pygame.Rect(
            WIDTH // 2 - box_w // 2, HEIGHT // 2 - box_h // 2, box_w, box_h
        )
        pygame.draw.rect(surf, PANEL_COLOR, box_rect, border_radius=16)
        pygame.draw.rect(surf, HTMX_COLOR, box_rect, width=2, border_radius=16)

        title = self.assets.big.render("PLEASE ROTATE DEVICE", True, HTMX_GLOW)
        blit_centered_x(surf, title, WIDTH / 2, HEIGHT / 2 - 70)

        sub = self.assets.med.render(
            "Turn your phone horizontally 🔄", True, TEXT_COLOR
        )
        blit_centered_x(surf, sub, WIDTH / 2, HEIGHT / 2)

        desc = self.assets.small.render(
            "htmx-invaders requires landscape orientation", True, MUTED_TEXT_COLOR
        )
        blit_centered_x(surf, desc, WIDTH / 2, HEIGHT / 2 + 50)
