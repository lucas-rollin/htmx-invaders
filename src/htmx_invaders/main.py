"""Entry point: pygame bootstrap and the main loop."""

import asyncio

import pygame

if __package__:
    from .assets import Assets
    from .audio import Audio
    from .background import Background
    from .game import Game
    from .settings import FPS, HEIGHT, IS_WASM, MAX_DT, TITLE, WIDTH
    from .touch import TouchControls
else:
    import sys
    from pathlib import Path

    _src = str(Path(__file__).resolve().parent.parent)
    if _src not in sys.path:
        sys.path.insert(0, _src)

    from htmx_invaders.assets import Assets
    from htmx_invaders.audio import Audio
    from htmx_invaders.background import Background
    from htmx_invaders.game import Game
    from htmx_invaders.settings import FPS, HEIGHT, IS_WASM, MAX_DT, TITLE, WIDTH
    from htmx_invaders.touch import TouchControls


def init_pygame():
    """Initialise pygame and return the display surface."""
    # Improve WASM audio in chromium
    pygame.mixer.pre_init(44100, -16, 2, 4096)
    try:
        pygame.mixer.SoundPatch()
    except (AttributeError, NotImplementedError, pygame.error):
        pass

    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
    pygame.display.set_caption(TITLE)
    return screen


def poll_events(touch_controls=None):
    """Return (keep_running, keys pressed this frame)."""
    running = True
    just_pressed = set()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            just_pressed.add(event.key)
            if event.key == pygame.K_ESCAPE and not IS_WASM:
                running = False
        if touch_controls:
            touch_controls.handle_event(event)
    return running, just_pressed


async def main():
    screen = init_pygame()
    clock = pygame.time.Clock()

    # These need the display (convert_alpha) and mixer, so build them after init.
    assets = Assets()
    audio = Audio()
    background = Background(assets)
    game = Game(assets, audio)
    touch_controls = TouchControls(assets)

    running = True
    while running:
        dt = min(clock.tick(FPS) / 1000.0, MAX_DT)

        running, just_pressed = poll_events(touch_controls)
        keys = touch_controls.update_inputs(
            pygame.key.get_pressed(), just_pressed, game.state
        )
        game.update(dt, keys, just_pressed)

        background.update(dt)
        background.draw(screen)
        game.draw(screen)
        touch_controls.draw(screen, game.state)
        pygame.display.flip()
        await asyncio.sleep(0)

    pygame.quit()


def run_game():
    asyncio.run(main())


if __name__ == "__main__":
    run_game()
