import random

import pygame
import pytest

from htmx_invaders.content import FRAMEWORKS, Effect
from htmx_invaders.entities import Bullet, Enemy, FloatingText, PowerUpDrop
from htmx_invaders.game import WAVE_CLEAR_DELAY
from htmx_invaders.settings import HEIGHT, MAX_LIVES, WIDTH
from htmx_invaders.states import GameState

from .conftest import Keys, effect_for, spec_for

DT = 0.001


def step(game, keys=None, pressed=(), dt=DT):
    game.update(dt, keys if keys is not None else Keys(), set(pressed))


def one_enemy(game, x=600, y=200):
    e = Enemy(0, 0, FRAMEWORKS[0])
    e.base_x, e.base_y = x, y
    game.formation.enemies = [e]
    return e


def bullet_on(rect, pierce=False):
    return Bullet(rect.centerx, rect.centery, -560, 0, (255, 255, 255), pierce)


def enemy_bullet_on_player(game):
    r = game.player.rect
    game.enemy_bullets.append(Bullet(r.centerx, r.centery, 280, 0, (255, 0, 0)))


@pytest.fixture
def no_drops(monkeypatch):
    monkeypatch.setattr(random, "random", lambda: 1.0)


# -- state machine -----------------------------------------------------------

def test_starts_on_menu_with_menu_music(game, audio):
    assert game.state is GameState.MENU
    assert audio.music == ["menu"]


def test_space_starts_game(game, audio):
    step(game, pressed=[pygame.K_SPACE])
    assert game.state is GameState.PLAYING
    assert len(game.formation) > 0
    assert game.player.lives == MAX_LIVES
    assert audio.music[-1] == "soundtrack"


def test_menu_ignores_other_keys(game):
    step(game, pressed=[pygame.K_r, pygame.K_a])
    assert game.state is GameState.MENU


def test_r_restarts_from_game_over(playing):
    playing.score = 500
    playing.state = GameState.GAME_OVER
    step(playing, pressed=[pygame.K_r])
    assert playing.state is GameState.PLAYING
    assert playing.score == 0 and playing.level == 1


def test_game_over_ignores_space(playing):
    playing.state = GameState.GAME_OVER
    step(playing, pressed=[pygame.K_SPACE])
    assert playing.state is GameState.GAME_OVER


# -- shooting & scoring ------------------------------------------------------

def test_space_fires_with_sound_once_per_cooldown(playing, audio):
    step(playing, pressed=[pygame.K_SPACE])
    step(playing, pressed=[pygame.K_SPACE])
    assert len(playing.player_bullets) == 1
    assert audio.played.count("shoot") == 1


def test_bullet_kills_enemy_and_scores(playing, audio, no_drops):
    e = one_enemy(playing)
    e2 = Enemy(1, 0, FRAMEWORKS[1])
    e2.base_x, e2.base_y = 900, 200
    playing.formation.enemies.append(e2)
    playing.level = 3
    playing.player_bullets.append(bullet_on(e.rect))

    step(playing)

    assert playing.score == 30
    assert len(playing.formation) == 1
    assert playing.player_bullets == []
    assert "enemy_killed" in audio.played
    assert len(playing.floaters) == 1


def test_pierce_bullet_survives_a_kill_but_loses_pierce(playing, no_drops):
    e = one_enemy(playing)
    playing.formation.enemies.append(Enemy(1, 0, FRAMEWORKS[1]))  # keep wave alive
    playing.formation.enemies[1].base_x, playing.formation.enemies[1].base_y = 900, 200
    b = bullet_on(e.rect, pierce=True)
    playing.player_bullets.append(b)

    step(playing)

    assert b.alive and not b.pierce_shot
    assert len(playing.formation) == 1


def test_kill_can_drop_powerup(playing, monkeypatch):
    monkeypatch.setattr(random, "random", lambda: 0.0)
    e = one_enemy(playing)
    playing.player_bullets.append(bullet_on(e.rect))
    step(playing)
    assert len(playing.powerup_drops) == 1


# -- waves -------------------------------------------------------------------

def test_clearing_last_enemy_starts_wave_clear_then_next_level(playing, no_drops):
    e = one_enemy(playing)
    playing.powerup_effects.append(effect_for(Effect.SHIELD))
    playing.player_bullets.append(bullet_on(e.rect))

    step(playing)
    assert playing.state is GameState.WAVE_CLEAR
    assert playing.flash_msg

    step(playing, dt=WAVE_CLEAR_DELAY + 0.1)
    assert playing.state is GameState.PLAYING
    assert playing.level == 2
    assert len(playing.formation) > 0
    assert playing.powerup_effects == []


# -- damage ------------------------------------------------------------------

def test_enemy_bullet_costs_a_life(playing, audio):
    enemy_bullet_on_player(playing)
    step(playing)
    assert playing.player.lives == MAX_LIVES - 1
    assert "player_damaged" in audio.played
    assert playing.enemy_bullets == []


def test_immunity_after_hit(playing):
    enemy_bullet_on_player(playing)
    step(playing)
    enemy_bullet_on_player(playing)
    step(playing)
    assert playing.player.lives == MAX_LIVES - 1  # second bullet absorbed


def test_shield_blocks_damage(playing, audio):
    playing.powerup_effects.append(effect_for(Effect.SHIELD))
    enemy_bullet_on_player(playing)
    step(playing)
    assert playing.player.lives == MAX_LIVES
    assert playing.enemy_bullets == []
    assert "player_damaged" not in audio.played


def test_last_life_lost_is_game_over(playing):
    playing.player.lives = 1
    enemy_bullet_on_player(playing)
    step(playing)
    assert playing.state is GameState.GAME_OVER


def test_enemy_reaching_player_line_is_instant_game_over(playing):
    e = one_enemy(playing)
    e.base_y = playing.player.y
    step(playing)
    assert playing.state is GameState.GAME_OVER
    assert playing.player.lives == 0


def test_fatal_hit_on_same_frame_as_last_kill_stays_game_over(playing, no_drops):
    playing.player.lives = 1
    e = one_enemy(playing)
    playing.player_bullets.append(bullet_on(e.rect))
    enemy_bullet_on_player(playing)

    step(playing)

    assert playing.state is GameState.GAME_OVER


# -- power-ups ---------------------------------------------------------------

def drop_on_player(game, effect):
    r = game.player.rect
    d = PowerUpDrop(r.x, r.y, spec_for(effect))
    d.bob_phase = 0  # x == base_x
    game.powerup_drops.append(d)


def test_pickup_adds_timed_effect(playing, audio):
    drop_on_player(playing, Effect.TRIPLE_SHOT)
    step(playing)
    assert [e.effect for e in playing.powerup_effects] == [Effect.TRIPLE_SHOT]
    assert "powerup" in audio.played
    assert playing.powerup_drops == []


def test_picking_same_effect_refreshes_instead_of_stacking(playing):
    drop_on_player(playing, Effect.SHIELD)
    step(playing)
    playing.powerup_effects[0].timer = 1.0
    drop_on_player(playing, Effect.SHIELD)
    step(playing)
    assert len(playing.powerup_effects) == 1
    assert playing.powerup_effects[0].timer > 5


def test_extra_life_capped(playing):
    playing.player.lives = MAX_LIVES - 1
    drop_on_player(playing, Effect.EXTRA_LIFE)
    step(playing)
    assert playing.player.lives == MAX_LIVES

    drop_on_player(playing, Effect.EXTRA_LIFE)
    step(playing)
    assert playing.player.lives == MAX_LIVES


def test_pushback_moves_swarm_up_only_after_it_has_dropped(playing):
    e = one_enemy(playing)
    y0 = e.base_y

    drop_on_player(playing, Effect.ENEMY_PUSHBACK)
    step(playing)
    assert e.base_y == pytest.approx(y0)

    playing.formation.total_drop = 36
    drop_on_player(playing, Effect.ENEMY_PUSHBACK)
    step(playing)
    assert e.base_y == pytest.approx(y0 - 36)


def test_expired_effects_are_removed(playing):
    playing.powerup_effects.append(effect_for(Effect.RAPID_FIRE))
    step(playing, dt=0.05)
    for _ in range(200):
        step(playing, dt=0.05)
    assert playing.powerup_effects == []


# -- rendering smoke tests ---------------------------------------------------

@pytest.mark.parametrize("state", list(GameState))
def test_draw_every_state_without_error(playing, state):
    playing.powerup_effects.append(effect_for(Effect.SHIELD))
    drop_on_player(playing, Effect.RAPID_FIRE)
    playing.floaters.append(FloatingText(10, 10, "hi", (1, 2, 3)))
    playing.state = state
    playing.draw(pygame.Surface((WIDTH, HEIGHT)))
