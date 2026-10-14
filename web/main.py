"""pygbag entry point (web build only)."""

import asyncio
import os
import sys
import traceback

# Make sure the folder holding the package is importable in the WASM runtime.
for _p in (
    os.getcwd(),
    os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else "",
):
    if _p and _p not in sys.path:
        sys.path.insert(0, _p)


async def _show_error(text):
    import pygame

    print(text, file=sys.stderr, flush=True)
    try:
        pygame.display.init()
        pygame.font.init()
        screen = pygame.display.get_surface() or pygame.display.set_mode((1280, 720))
        font = pygame.font.Font(None, 22)
        lines = ["htmx invaders failed to start:", ""] + text.splitlines()[-28:]
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            screen.fill((40, 0, 0))
            for i, line in enumerate(lines):
                screen.blit(
                    font.render(line[:150], True, (255, 220, 220)), (16, 12 + i * 22)
                )
            pygame.display.flip()
            await asyncio.sleep(0)
    except Exception:  # noqa: BLE001
        traceback.print_exc()


async def boot():
    try:
        from htmx_invaders.main import main

        await main()
    except Exception:  # noqa: BLE001
        await _show_error(traceback.format_exc())


asyncio.run(boot())
