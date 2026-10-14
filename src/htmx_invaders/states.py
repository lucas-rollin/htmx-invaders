from enum import Enum, auto


class GameState(Enum):
    MENU = auto()
    PLAYING = auto()
    WAVE_CLEAR = auto()
    GAME_OVER = auto()
