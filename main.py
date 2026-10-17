"""Top-level entrypoint for local execution and PyInstaller bundling."""

import sys
from pathlib import Path

# Ensure src/ is on sys.path for direct execution and PyInstaller analysis
_src = str(Path(__file__).resolve().parent / "src")
if _src not in sys.path:
    sys.path.insert(0, _src)

from htmx_invaders.main import run_game

if __name__ == "__main__":
    run_game()
