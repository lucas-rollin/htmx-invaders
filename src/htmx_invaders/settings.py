"""Static configuration: screen, colors and global tuning constants."""

TITLE = "htmx vs The JS Fatigue"
WIDTH, HEIGHT = 1280, 720
FPS = 60
MAX_DT = 0.05  # clamp frame time so lag spikes don't tunnel through things

# Colors
BG_COLOR = (18, 18, 28)
GRID_COLOR = (140, 140, 175)
PANEL_COLOR = (24, 24, 34)
MUTED_TEXT_COLOR = (150, 150, 165)
HTMX_COLOR = (59, 130, 246)
HTMX_GLOW = (147, 197, 253)
TEXT_COLOR = (220, 220, 235)
DANGER_COLOR = (239, 68, 68)
GOOD_COLOR = (52, 211, 153)

# Gameplay
MAX_LIVES = 3
POWERUP_DROP_CHANCE = 0.05
LOGO_SIZE = 30
