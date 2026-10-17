"""Game rules and state machine. Rendering lives in `screens` and the entities."""

import random

import pygame

from . import screens
from .content import JOKES, WAVE_CLEAR_MESSAGES, Effect, random_powerup
from .entities import (
    Bullet,
    FloatingText,
    Player,
    PowerUpDrop,
    PowerUpEffect,
    has_effect,
)
from .formation import Formation
from .settings import GOOD_COLOR, MAX_LIVES, POWERUP_DROP_CHANCE
from .states import GameState

WAVE_CLEAR_DELAY = 2.2


def _alive(items):
    return [i for i in items if i.alive]


class Game:
    def __init__(self, assets, audio):
        self.assets = assets
        self.audio = audio

        self.state = GameState.MENU
        self.score = 0
        self.level = 1
        self.player = Player()
        self.formation = Formation()
        self.powerup_drops: list[PowerUpDrop] = []
        self.powerup_effects: list[PowerUpEffect] = []
        self.player_bullets: list[Bullet] = []
        self.enemy_bullets: list[Bullet] = []
        self.floaters: list[FloatingText] = []
        self.enemy_shoot_timer = 0.0
        self.message_timer = 0.0
        self.flash_msg = ""

        audio.play_menu_music()

    # -- lifecycle ---------------------------------------------------------
    def reset(self):
        self.score = 0
        self.level = 1
        self.player = Player()
        self.floaters = []
        self.powerup_drops = []
        self.powerup_effects = []
        self._start_wave()
        self.state = GameState.PLAYING
        self.audio.play_random_soundtrack()

    def to_menu(self):
        self.state = GameState.MENU
        self.score = 0
        self.level = 1
        self.player = Player()
        self.formation = Formation()
        self.player_bullets = []
        self.enemy_bullets = []
        self.powerup_drops = []
        self.powerup_effects = []
        self.floaters = []
        self.enemy_shoot_timer = 0.0
        self.message_timer = 0.0
        self.flash_msg = ""
        self.audio.play_menu_music()

    def _start_wave(self):
        self.formation.spawn(self.level)
        self.player_bullets = []
        self.enemy_bullets = []

    # -- update ------------------------------------------------------------
    def update(self, dt, keys, just_pressed):
        if pygame.K_ESCAPE in just_pressed and self.state is not GameState.MENU:
            self.to_menu()
            return

        if self.state is GameState.MENU:
            if pygame.K_SPACE in just_pressed:
                self.reset()
        elif self.state is GameState.GAME_OVER:
            if pygame.K_r in just_pressed:
                self.reset()
        elif self.state is GameState.WAVE_CLEAR:
            self._update_wave_clear(dt)
        else:
            self._update_playing(dt, keys, just_pressed)

    def _update_wave_clear(self, dt):
        self.message_timer -= dt
        if self.message_timer <= 0:
            self.level += 1
            self._start_wave()
            self.powerup_drops = []
            self.powerup_effects = []
            self.state = GameState.PLAYING

    def _update_playing(self, dt, keys, just_pressed):
        self.player.update(dt, keys)
        if pygame.K_SPACE in just_pressed:
            bullets = self.player.try_shoot(self.powerup_effects)
            if bullets:
                self.audio.play("shoot")
                self.player_bullets.extend(bullets)

        for group in (
            self.powerup_drops,
            self.powerup_effects,
            self.player_bullets,
            self.enemy_bullets,
        ):
            for item in group:
                item.update(dt)
        self.powerup_drops = _alive(self.powerup_drops)
        self.powerup_effects = [p for p in self.powerup_effects if p.active]
        self.player_bullets = _alive(self.player_bullets)
        self.enemy_bullets = _alive(self.enemy_bullets)

        self.formation.update(dt)
        self._enemy_fire(dt)

        self._player_bullets_vs_enemies()
        self._enemy_bullets_vs_player()
        self._player_vs_powerups()

        for f in self.floaters:
            f.update(dt)
        self.floaters = _alive(self.floaters)

        # lose condition: an enemy reaches the player's line
        if self.formation.reached(self.player.y):
            self._lose_life(fatal=True)

        if self.state is GameState.PLAYING and not self.formation:
            self.state = GameState.WAVE_CLEAR
            self.message_timer = WAVE_CLEAR_DELAY
            self.flash_msg = random.choice(WAVE_CLEAR_MESSAGES)

    def _enemy_fire(self, dt):
        self.enemy_shoot_timer -= dt
        if self.enemy_shoot_timer <= 0 and self.formation:
            self.enemy_shoot_timer = max(0.25, 0.9 - self.level * 0.05)
            shooter = random.choice(self.formation.enemies)
            cx = shooter.x + shooter.WIDTH / 2
            cy = shooter.y + shooter.HEIGHT
            self.enemy_bullets.append(Bullet(cx, cy, 280, 0, shooter.fw.color))

    # -- collisions --------------------------------------------------------
    def _player_bullets_vs_enemies(self):
        for b in self.player_bullets:
            if not b.alive:
                continue
            for e in self.formation:
                if e.alive and b.rect.colliderect(e.rect):
                    self._kill_enemy(e, b)
                    break
        self.formation.remove_dead()
        self.player_bullets = _alive(self.player_bullets)

    def _kill_enemy(self, enemy, bullet):
        enemy.alive = False
        if bullet.pierce_shot:
            bullet.pierce_shot = False  # a pierce shot is spent after one extra kill
        else:
            bullet.alive = False

        self.audio.play("enemy_killed")
        self.score += 10 * self.level
        self.floaters.append(
            FloatingText(
                enemy.x + enemy.WIDTH / 2, enemy.y, random.choice(JOKES), enemy.fw.color
            )
        )
        if random.random() < POWERUP_DROP_CHANCE:
            self.powerup_drops.append(
                PowerUpDrop(
                    enemy.base_x + enemy.WIDTH / 2,
                    enemy.base_y + enemy.HEIGHT / 2,
                    random_powerup(),
                )
            )

    def _enemy_bullets_vs_player(self):
        pr = self.player.rect
        shielded = has_effect(self.powerup_effects, Effect.SHIELD)
        for b in self.enemy_bullets:
            if b.alive and b.rect.colliderect(pr):
                b.alive = False
                if not shielded and self.player.immunity <= 0:
                    self._lose_life()
                    self.audio.play("player_damaged")
        self.enemy_bullets = _alive(self.enemy_bullets)

    def _player_vs_powerups(self):
        pr = self.player.rect
        for p in self.powerup_drops:
            if p.alive and p.rect.colliderect(pr):
                p.alive = False
                self._apply_powerup(p.spec)
                self.audio.play("powerup")
                self.floaters.append(
                    FloatingText(
                        p.x + p.WIDTH / 2,
                        p.y,
                        p.spec.effect.value.replace("_", " "),
                        p.spec.color,
                    )
                )
        self.powerup_drops = _alive(self.powerup_drops)

    # -- rules -------------------------------------------------------------
    def _apply_powerup(self, spec):
        if spec.effect is Effect.EXTRA_LIFE and self.player.lives < MAX_LIVES:
            self.player.lives += 1
            return
        if spec.effect is Effect.ENEMY_PUSHBACK and self.formation.push_back():
            return

        for active in self.powerup_effects:
            if active.effect == spec.effect:
                active.refresh(spec)
                return
        self.powerup_effects.append(PowerUpEffect(spec))

    def _lose_life(self, fatal=False):
        self.player.take_hit(fatal)
        if self.player.lives <= 0:
            self.state = GameState.GAME_OVER

    # -- draw --------------------------------------------------------------
    def draw(self, surf):
        if self.state is GameState.MENU:
            screens.draw_menu(surf, self.assets)
            return

        a = self.assets
        for p in self.powerup_drops:
            p.draw(surf, a)
        for e in self.formation:
            e.draw(surf, a)
        for b in self.player_bullets:
            b.draw(surf)
        for b in self.enemy_bullets:
            b.draw(surf)
        self.player.draw(surf, a, self.powerup_effects)
        for f in self.floaters:
            f.draw(surf, a)

        screens.draw_hud(
            surf, a, self.score, self.level, self.powerup_effects, self.player.lives
        )

        if self.state is GameState.WAVE_CLEAR:
            screens.draw_wave_clear(surf, a, self.flash_msg, GOOD_COLOR)
        elif self.state is GameState.GAME_OVER:
            screens.draw_game_over(surf, a, self.score)
