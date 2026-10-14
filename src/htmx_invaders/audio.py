"""Sound effects and music."""

import os
import random

import pygame

from .content import MENU_SOUNDTRACK, SOUNDTRACKS
from .paths import SFX_DIR

# name -> (file, volume)
_SFX = {
    "shoot": ("shoot.ogg", 0.15),
    "enemy_killed": ("enemy_killed.ogg", 0.1),
    "powerup": ("powerup.ogg", 0.6),
    "player_damaged": ("explosion.ogg", 0.3),
}
_MUSIC_VOLUME = 0.8


class Audio:
    def __init__(self):
        self._sounds = {}
        for name, (file, volume) in _SFX.items():
            sound = pygame.mixer.Sound(os.path.join(SFX_DIR, file))
            sound.set_volume(volume)
            self._sounds[name] = sound

    def play(self, name):
        self._sounds[name].play()

    def play_menu_music(self):
        self._play_music(MENU_SOUNDTRACK)

    def play_random_soundtrack(self):
        self._play_music(random.choice(SOUNDTRACKS))

    @staticmethod
    def _play_music(file):
        pygame.mixer.music.load(os.path.join(SFX_DIR, file))
        pygame.mixer.music.set_volume(_MUSIC_VOLUME)
        pygame.mixer.music.play(-1)
