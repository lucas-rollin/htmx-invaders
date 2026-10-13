"""Game content: the data that defines enemies, power-ups and flavour text."""

import random
from dataclasses import dataclass
from enum import Enum

from .settings import HTMX_COLOR

Color = tuple[int, int, int]


@dataclass(frozen=True)
class Framework:
    name: str
    color: Color
    file: str


FRAMEWORKS = (
    Framework("React",   (97, 218, 251),  "react.png"),
    Framework("Vue",     (66, 184, 131),  "vue.png"),
    Framework("Angular", (234, 33, 162),  "angular.png"),
    Framework("Redux",   (147, 100, 209), "redux.png"),
    Framework("Svelte",  (255, 98, 0),    "svelte.png"),
    Framework("npm",     (196, 54, 53),   "npm.png"),
    Framework("Vite",    (154, 100, 255), "vite.png"),
    Framework("Webpack", (137, 206, 242), "webpack.png"),
    Framework("Babel",   (245, 207, 90),  "babel.png"),
)


class Effect(str, Enum):
    EXTRA_LIFE = "extra_life"
    RAPID_FIRE = "rapid_fire"
    TRIPLE_SHOT = "triple_shot"
    PIERCE_SHOT = "pierce_shot"
    SHIELD = "shield"
    ENEMY_PUSHBACK = "enemy_pushback"


@dataclass(frozen=True)
class PowerUpSpec:
    name: str
    color: Color
    symbol: str
    effect: Effect
    timer: float  # seconds the effect lasts; 0 = instant
    weight: int   # relative drop probability


POWERUPS = (
    PowerUpSpec("+1 life",    HTMX_COLOR,       "</>", Effect.EXTRA_LIFE,     0, 1),
    PowerUpSpec("hx-boost",   HTMX_COLOR,       "b",   Effect.RAPID_FIRE,     8, 3),
    PowerUpSpec("hx-trigger", HTMX_COLOR,       "t",   Effect.TRIPLE_SHOT,    8, 2),
    PowerUpSpec("vanilla.js", (239, 216, 29),   "JS",  Effect.PIERCE_SHOT,    8, 3),
    PowerUpSpec("alpine.js",  (145, 190, 198),  "v",   Effect.SHIELD,         6, 2),
    PowerUpSpec("hx-swap",    HTMX_COLOR,       "^",   Effect.ENEMY_PUSHBACK, 0, 2),
)


def random_powerup() -> PowerUpSpec:
    return random.choices(POWERUPS, weights=[p.weight for p in POWERUPS])[0]


JOKES = (
    "npm install regret",
    "another breaking change",
    "left-pad strikes again",
    "node_modules: 1.2GB",
    "deprecated in v2",
    "just use fetch()",
    "no virtual DOM needed",
    "hypermedia wins",
    "fatigue -1",
    "config? what config?",
    "build step eliminated",
    "0kb runtime added",
    "zero hydration achieved",
    "rm -rf node_modules",
    "callback hell reborn",
    "is this even JavaScript?",
    "just add another dependency",
    "hypermedia > JSON",
    "server rendering is back",
    "client state? never heard of",
    "single-page apps in shambles",
    "localStorage is not a database",
    "bundler of the week",
    "your stack is outdated",
    "REST in peace",
    "just send HTML",
)

WAVE_CLEAR_MESSAGES = ("WAVE SIMPLIFIED", "FATIGUE REDUCED", "SWARM PATCHED OUT")

SOUNDTRACKS = ("a-hero-of-the-80s.ogg", "retro-lounge.ogg", "retro.ogg")
MENU_SOUNDTRACK = "menu.ogg"
