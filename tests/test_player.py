import pygame
import pytest

from htmx_invaders.content import Effect
from htmx_invaders.entities import Player
from htmx_invaders.settings import MAX_LIVES, WIDTH

from .conftest import Keys, effect_for


def test_moves_right_and_left():
    p = Player()
    x0 = p.x
    p.update(0.1, Keys({pygame.K_RIGHT: True}))
    assert p.x == pytest.approx(x0 + Player.SPEED * 0.1)
    p.update(0.1, Keys({pygame.K_a: True}))
    assert p.x == pytest.approx(x0)


def test_opposite_keys_cancel():
    p = Player()
    x0 = p.x
    p.update(0.1, Keys({pygame.K_LEFT: True, pygame.K_RIGHT: True}))
    assert p.x == x0


def test_clamped_to_screen():
    p = Player()
    p.update(100, Keys({pygame.K_LEFT: True}))
    assert p.x == 10
    p.update(100, Keys({pygame.K_RIGHT: True}))
    assert p.x == WIDTH - Player.WIDTH - 10


def test_shoots_one_upward_bullet():
    p = Player()
    (b,) = p.try_shoot([])
    assert b.vy < 0 and b.vx == 0
    assert not b.pierce_shot


def test_cooldown_blocks_then_releases():
    p = Player()
    assert p.try_shoot([])
    assert p.try_shoot([]) == []
    p.update(Player.COOLDOWN + 0.01, Keys())
    assert p.try_shoot([])


def test_rapid_fire_halves_cooldown():
    p = Player()
    p.try_shoot([effect_for(Effect.RAPID_FIRE)])
    assert p.cooldown_left == pytest.approx(Player.COOLDOWN / 2)


def test_triple_shot_spreads():
    bullets = Player().try_shoot([effect_for(Effect.TRIPLE_SHOT)])
    assert sorted(b.vx for b in bullets) == [-Player.SPREAD_SPEED, 0, Player.SPREAD_SPEED]


def test_pierce_flag_propagates_to_all_bullets():
    bullets = Player().try_shoot(
        [effect_for(Effect.PIERCE_SHOT), effect_for(Effect.TRIPLE_SHOT)]
    )
    assert len(bullets) == 3 and all(b.pierce_shot for b in bullets)


def test_take_hit():
    p = Player()
    p.take_hit()
    assert p.lives == MAX_LIVES - 1
    assert p.immunity > 0 and p.hit_flash > 0


def test_fatal_hit_zeroes_lives():
    p = Player()
    p.take_hit(fatal=True)
    assert p.lives == 0


def test_timers_never_go_negative():
    p = Player()
    p.take_hit()
    p.update(100, Keys())
    assert p.immunity == 0 and p.hit_flash == 0 and p.cooldown_left == 0
