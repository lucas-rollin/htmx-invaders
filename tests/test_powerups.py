import random
from collections import Counter

from htmx_invaders.content import POWERUPS, Effect, random_powerup
from htmx_invaders.entities import PowerUpDrop, PowerUpEffect, has_effect
from htmx_invaders.settings import HEIGHT

from .conftest import effect_for, spec_for


def test_effect_expires_after_timer():
    e = effect_for(Effect.SHIELD)
    e.update(spec_for(Effect.SHIELD).timer - 0.1)
    assert e.active
    e.update(0.2)
    assert not e.active


def test_refresh_resets_timer():
    spec = spec_for(Effect.RAPID_FIRE)
    e = PowerUpEffect(spec)
    e.update(5)
    e.refresh(spec)
    assert e.timer == spec.timer


def test_instant_effects_expire_immediately():
    e = effect_for(Effect.EXTRA_LIFE)
    e.update(0.001)
    assert not e.active


def test_has_effect():
    effects = [effect_for(Effect.SHIELD)]
    assert has_effect(effects, Effect.SHIELD)
    assert not has_effect(effects, Effect.TRIPLE_SHOT)
    assert not has_effect([], Effect.SHIELD)


def test_random_powerup_covers_all_and_respects_weights():
    random.seed(1234)
    counts = Counter(random_powerup().effect for _ in range(5000))
    assert set(counts) == {p.effect for p in POWERUPS}
    # weight 3 should clearly beat weight 1
    assert counts[Effect.RAPID_FIRE] > counts[Effect.EXTRA_LIFE]


def test_drop_falls_and_despawns_below_screen():
    d = PowerUpDrop(100, 0, spec_for(Effect.SHIELD))
    y0 = d.y
    d.update(0.1)
    assert d.y > y0 and d.alive
    d.update(HEIGHT)  # fall far past the bottom
    assert not d.alive
