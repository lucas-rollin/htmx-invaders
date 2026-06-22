import os
import sys
import math
import random
import asyncio

import pygame

# ----------------------------------------------------------------------------
# Setup
# ----------------------------------------------------------------------------

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller."""
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

pygame.init()

WIDTH, HEIGHT = 1280, 720
FPS = 60

screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.SCALED)
pygame.display.set_caption("htmx vs The JS Fatigue")
clock = pygame.time.Clock()

FONT_PATH = resource_path(os.path.join("assets", "fonts", "SpaceMono-Regular.ttf"))

def get_font(size, bold=False):
    f = pygame.font.Font(FONT_PATH, size)
    f.set_bold(bold)
    return f


FONT_BIG = get_font(56, bold=True)
FONT_MED = get_font(28, bold=True)
FONT_SMALL = get_font(18)
FONT_TINY = get_font(14)

# Colors
BG_COLOR = (18, 18, 28)
GRID_COLOR = (140, 140, 175)
HTMX_COLOR = (59, 130, 246)
HTMX_GLOW = (147, 197, 253)
TEXT_COLOR = (220, 220, 235)
DANGER_COLOR = (239, 68, 68)
GOOD_COLOR = (52, 211, 153)


FRAMEWORKS = [
    {"name": "React",   "color": (97, 218, 251),    "file": "react.png"},
    {"name": "Vue",     "color": (66, 184, 131),    "file": "vue.png"},
    {"name": "Angular", "color": (234, 33, 162),    "file": "angular.png"},
    {"name": "Redux",   "color": (147, 100, 209),   "file": "redux.png"},
    {"name": "Svelte",  "color": (255, 98, 0),      "file": "svelte.png"},
    {"name": "npm",     "color": (196, 54, 53),     "file": "npm.png"},
    {"name": "Vite",    "color": (154, 100, 255),   "file": "vite.png"},
    {"name": "Webpack", "color": (137, 206, 242),   "file": "webpack.png"},
    {"name": "Babel",   "color": (245, 207, 90),    "file": "babel.png"},
]

POWERUP_DROP_CHANCE = 0.05

POWERUPS = [
    {
        "name": "+1 life", 
        "color": HTMX_COLOR,
        "symbol": "</>",
        "effect": "extra_life", 
        "timer": 0,
        "spawn_rate_weight": 1
    },
    {
        "name": "hx-boost", 
        "color": HTMX_COLOR, 
        "symbol": "b", 
        "effect": "rapid_fire", 
        "timer": 8,
        "spawn_rate_weight": 3
    },
    {
        "name": "hx-trigger", 
        "color": HTMX_COLOR, 
        "symbol": "t", 
        "effect": "triple_shot", 
        "timer": 8,
        "spawn_rate_weight": 2
    },
    {
        "name": "vanilla.js", 
        "color": (239, 216, 29),  
        "symbol": "JS",   
        "effect": "pierce_shot", 
        "timer": 8,
        "spawn_rate_weight": 3
    }, 
    {
        "name": "alpine.js", 
        "color": (145, 190, 198), 
        "symbol": "v", 
        "effect": "shield", 
        "timer": 6,
        "spawn_rate_weight": 2
    },
    {
        "name": "hx-swap", 
        "color": HTMX_COLOR, 
        "symbol": "^", 
        "effect": "enemy_pushback", 
        "timer": 0,
        "spawn_rate_weight": 2
    },                
]

IMG_DIR = resource_path(os.path.join("assets", "img"))
LOGO_SIZE = 30 

def load_enemy_logos():
    """Load PNGs for each framework."""
    for fw in FRAMEWORKS:
        path = os.path.join(IMG_DIR, fw["file"])
        fw["image"] = None
        try:
            img = pygame.image.load(path).convert_alpha()
            w, h = img.get_size()
            scale = LOGO_SIZE / max(w, h)
            new_size = (max(1, round(w * scale)), max(1, round(h * scale)))
            fw["image"] = pygame.transform.smoothscale(img, new_size)
        except (pygame.error, OSError) as e:
            print(f"[htmx_invaders] couldn't load {path}: {e}")


load_enemy_logos()

JOKES = [
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
]

STATE_MENU = "menu"
STATE_PLAYING = "playing"
STATE_WAVE_CLEAR = "wave_clear"
STATE_GAME_OVER = "game_over"

# ----------------------------------------------------------------------------
# Background starfield (little floating angle-bracket / brace particles)
# ----------------------------------------------------------------------------

BG_GLYPHS = ["<", ">", "/", "{", "}", ";"]


class BgParticle:
    def __init__(self):
        self.x = random.uniform(0, WIDTH)
        self.y = random.uniform(0, HEIGHT)
        self.speed = random.uniform(10, 35)
        self.glyph = random.choice(BG_GLYPHS)
        self.alpha = random.randint(20, 60)
        self.size = random.randint(12, 22)

    def update(self, dt):
        self.y += self.speed * dt
        if self.y > HEIGHT + 20:
            self.y = -20
            self.x = random.uniform(0, WIDTH)

    def draw(self, surf):
        f = get_font(self.size)
        img = f.render(self.glyph, True, GRID_COLOR)
        img.set_alpha(self.alpha)
        surf.blit(img, (self.x, self.y))


bg_particles = [BgParticle() for _ in range(100)]


def draw_background(dt):
    screen.fill(BG_COLOR)
    for p in bg_particles:
        p.update(dt)
        p.draw(screen)


# ----------------------------------------------------------------------------
# Sound Effects
# ----------------------------------------------------------------------------

SFX_DIR = os.path.join("assets", "sfx")

SOUNTRACK_PATHS = [
    "a-hero-of-the-80s.ogg",
    "retro-lounge.ogg",
    "retro.ogg",
]

MENU_SOUNDTRACK = "menu.ogg"

shoot_sound = pygame.mixer.Sound(resource_path(os.path.join(SFX_DIR, "shoot.ogg")))
shoot_sound.set_volume(0.15) 
enemy_killed_sound = pygame.mixer.Sound(resource_path(os.path.join(SFX_DIR, "enemy_killed.ogg")))
enemy_killed_sound.set_volume(0.1)
powerup_sound = pygame.mixer.Sound(resource_path(os.path.join(SFX_DIR, "powerup.ogg")))
powerup_sound.set_volume(0.6)
player_damaged_sound = pygame.mixer.Sound(resource_path(os.path.join(SFX_DIR, "explosion.ogg")))
player_damaged_sound.set_volume(0.3)

def play_menu_music():
    pygame.mixer.music.load(resource_path(os.path.join(SFX_DIR, MENU_SOUNDTRACK)))
    pygame.mixer.music.set_volume(0.8)
    pygame.mixer.music.play(-1)

def play_random_soundtrack():
    soundtrack = random.choice(SOUNTRACK_PATHS)
    pygame.mixer.music.load(resource_path(os.path.join(SFX_DIR, soundtrack)))
    pygame.mixer.music.set_volume(0.8)
    pygame.mixer.music.play(-1)

# ----------------------------------------------------------------------------
# Entities
# ----------------------------------------------------------------------------


class Player:
    WIDTH = 70
    HEIGHT = 36
    SPEED = 360
    COOLDOWN = 0.28

    def __init__(self):
        self.x = WIDTH / 2 - self.WIDTH / 2
        self.y = HEIGHT - 70
        self.cooldown_left = 0.0
        self.lives = 3
        self.hit_flash = 0.0
        self.immunity = 0.0

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.WIDTH, self.HEIGHT)

    def update(self, dt, keys):
        dx = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx += 1
        self.x += dx * self.SPEED * dt
        self.x = max(10, min(WIDTH - self.WIDTH - 10, self.x))

        if self.cooldown_left > 0:
            self.cooldown_left -= dt
        if self.hit_flash > 0:
            self.hit_flash -= dt
        if self.immunity > 0:
            self.immunity -= dt

    def try_shoot(self, powerup_effects):
        rapid_fire = any(p.effect == "rapid_fire" for p in powerup_effects)
        pierce_shot = any(p.effect == "pierce_shot" for p in powerup_effects)
        triple_shot = any(p.effect == "triple_shot" for p in powerup_effects)

        if rapid_fire:
            cooldown = self.COOLDOWN / 2
        else:
            cooldown = self.COOLDOWN

        if self.cooldown_left <= 0:
            self.cooldown_left = cooldown
            cx = self.x + self.WIDTH / 2
            shoot_sound.play()
            if triple_shot:
                return [
                    Bullet(cx, self.y - 6, -560,    0, HTMX_COLOR, pierce_shot),
                    Bullet(cx, self.y - 6, -560,  150, HTMX_COLOR, pierce_shot),
                    Bullet(cx, self.y - 6, -560, -150, HTMX_COLOR, pierce_shot),
                ]
            else:
                return [Bullet(cx, self.y - 6, -560, 0, HTMX_COLOR, pierce_shot)]
        return [None]

    def draw(self, surf, powerup_effects=[]):
        r = self.rect
        color = DANGER_COLOR if self.hit_flash > 0 else HTMX_COLOR

        # Draw shield powerup
        shield = next((p for p in powerup_effects if p.effect == "shield"), None)
        if shield:
            if shield.timer < 2:
                pulse = (math.sin(pygame.time.get_ticks() / 50) + 1) / 2
                alpha = int(70 * pulse)
            else:
                alpha = 40
            glow = pygame.Surface((r.width + 24, r.height + 24), pygame.SRCALPHA)
            pygame.draw.rect(
                glow, (*HTMX_GLOW, alpha), glow.get_rect(), border_radius=14
            )
            surf.blit(glow, (r.x - 12, r.y - 12))

        pygame.draw.rect(surf, (28, 28, 40), r, border_radius=8)
        pygame.draw.rect(surf, color, r, width=2, border_radius=8)
        label = FONT_MED.render("</>", True, color)
        surf.blit(
            label,
            (r.centerx - label.get_width() // 2, r.centery - label.get_height() // 2),
        )
        # little engine flicker
        flame_h = random.randint(4, 10)
        pygame.draw.polygon(
            surf,
            (255, 200, 90),
            [
                (r.centerx - 6, r.bottom),
                (r.centerx + 6, r.bottom),
                (r.centerx, r.bottom + flame_h),
            ],
        )


class Bullet:
    def __init__(self, x, y, vy, vx, color, pierce_shot=False, width=4, height=14):
        self.x = x
        self.y = y
        self.vy = vy
        self.vx = vx
        self.color = color
        self.pierce_shot = pierce_shot
        self.width = width
        self.height = height
        self.alive = True

    @property
    def rect(self):
        return pygame.Rect(
            int(self.x - self.width / 2), int(self.y - self.height / 2),
            self.width, self.height,
        )

    def update(self, dt):
        self.y += self.vy * dt
        self.x += self.vx * dt
        if self.y < -20 or self.y > HEIGHT + 20:
            self.alive = False

    def draw(self, surf):
        color = DANGER_COLOR if self.pierce_shot else self.color
        pygame.draw.rect(surf, color, self.rect, border_radius=2)


class PowerUpDrop:
    WIDTH = 30
    HEIGHT = 30

    def __init__(self, x, y):
        self.base_x = x
        self.y = y
        self.vy = random.uniform(120, 200)
        self.bob_phase = random.uniform(0, math.tau)
        self.alive = True

        weights = [p["spawn_rate_weight"] for p in POWERUPS]
        chosen_power = random.choices(POWERUPS, weights=weights)
        self.power = chosen_power[0]

    @property
    def x(self):
        return self.base_x + math.sin(self.bob_phase) * 30

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.WIDTH, self.HEIGHT)

    def update(self, dt):
        self.bob_phase += dt * 2
        self.y += self.vy * dt
        if self.y < -20:
            self.alive = False

    def draw(self, surf):
        r = self.rect
        pulse = (math.sin(pygame.time.get_ticks() / 250) + 1) / 2
        start_color = tuple(
            int(self.power["color"][c] + (255 - self.power["color"][c]) * pulse * 0.5) for c in range(3)
        )
        pygame.draw.rect(surf, (24, 24, 34), r, border_radius=10)
        pygame.draw.rect(surf, start_color, r, width=2, border_radius=10)

        label = FONT_TINY.render(self.power["symbol"], True, start_color)
        surf.blit(
            label,
            (r.centerx - label.get_width() // 2, r.centery - label.get_height() // 2),
        )

        name = FONT_TINY.render(self.power["name"], True, (150, 150, 165))
        surf.blit(name, (r.centerx - name.get_width() // 2, r.bottom + 1))


class PowerUpEffect:
    def __init__(self, power):
        self.effect = power["effect"]
        self.timer = power["timer"]
        self.symbol = power["symbol"]
        self.color = power["color"]
        self.active = True
        self.width = FONT_SMALL.size(self.symbol)[0]

    def update(self, dt):
        self.timer -= dt
        if self.timer < 0:
            self.active = False 

    def draw(self, surf, x, y):
        if self.timer < 2:
            pulse = (math.sin(pygame.time.get_ticks() / 50) + 1) / 2
            alpha = int(255 * pulse)
        else:
            alpha = 255

        p = FONT_SMALL.render(self.symbol, True, self.color)
        
        p.set_alpha(alpha)
        surf.blit(p, (x, y))


class Enemy:
    WIDTH = 52
    HEIGHT = 40

    def __init__(self, col, row, fw):
        self.col = col
        self.row = row
        self.fw = fw
        self.base_x = 0.0  # set by formation
        self.base_y = 0.0
        self.bob_phase = random.uniform(0, math.tau)
        self.alive = True

    @property
    def x(self):
        return self.base_x

    @property
    def y(self):
        return self.base_y + math.sin(self.bob_phase) * 3

    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.WIDTH, self.HEIGHT)

    def update(self, dt):
        self.bob_phase += dt * 2

    def draw(self, surf):
        r = self.rect
        pygame.draw.rect(surf, (24, 24, 34), r, border_radius=10)
        pygame.draw.rect(surf, self.fw["color"], r, width=2, border_radius=10)

        img = self.fw.get("image")
        surf.blit(
            img,
            (r.centerx - img.get_width() // 2, r.centery - img.get_height() // 2 - 2),
        )

        name = FONT_TINY.render(self.fw["name"], True, (150, 150, 165))
        surf.blit(name, (r.centerx - name.get_width() // 2, r.bottom + 1))


class FloatingText:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 1.0

    def update(self, dt):
        self.y -= 30 * dt
        self.life -= dt * 0.9

    @property
    def alive(self):
        return self.life > 0

    def draw(self, surf):
        img = FONT_TINY.render(self.text, True, self.color)
        img.set_alpha(max(0, int(255 * self.life)))
        surf.blit(img, (self.x - img.get_width() / 2, self.y))


# ----------------------------------------------------------------------------
# Game state
# ----------------------------------------------------------------------------


class Game:
    ENEMY_DROP_RATE = 18
    
    def __init__(self):
        self.state = STATE_MENU

        play_menu_music()

        self.score = 0
        self.level = 1
        self.player = Player()
        self.powerup_drops = []
        self.powerup_effects = []
        self.player_bullets = []
        self.enemy_bullets = []
        self.enemies = []
        self.floaters = []
        self.formation_dx = 60.0  # px/sec, horizontal drift of the swarm
        self.formation_drop = 0.0
        self.enemy_shoot_timer = 0.0
        self.message_timer = 0.0
        self.flash_msg = ""
        

    # -- wave setup --------------------------------------------------------
    def spawn_wave(self):
        self.enemies = []
        rows = min(3 + (self.level - 1) // 2, 7)
        cols = min(6 + (self.level - 1), 16)
        spacing_x = 64
        spacing_y = 58
        total_w = cols * spacing_x
        start_x = (WIDTH - total_w) / 2 + spacing_x / 2 - Enemy.WIDTH / 2
        start_y = 70

        for row in range(rows):
            for col in range(cols):
                fw = random.choice(FRAMEWORKS)
                e = Enemy(col, row, fw)
                e.base_x = start_x + col * spacing_x
                e.base_y = start_y + row * spacing_y
                self.enemies.append(e)

        self.formation_dx = 50.0 + self.level * 8.0
        self.formation_drop = 0.0
        self.player_bullets = []
        self.enemy_bullets = []

    def reset(self):
        self.score = 0
        self.level = 1
        self.player = Player()
        self.floaters = []
        self.spawn_wave()
        self.powerup_drops = []
        self.powerup_effects = []
        self.state = STATE_PLAYING

        play_random_soundtrack()

    # -- update --------------------------------------------------------
    def update(self, dt, keys, just_pressed):
        if self.state == STATE_MENU:
            if pygame.K_SPACE in just_pressed:
                self.reset()
            return

        if self.state == STATE_GAME_OVER:
            if pygame.K_r in just_pressed:
                self.reset()
            return

        if self.state == STATE_WAVE_CLEAR:
            self.message_timer -= dt
            if self.message_timer <= 0:
                self.level += 1
                self.spawn_wave()
                self.powerup_drops = []
                self.powerup_effects = []
                self.state = STATE_PLAYING
            return

        # STATE_PLAYING
        self.player.update(dt, keys)
        if pygame.K_SPACE in just_pressed:
            bullets = self.player.try_shoot(self.powerup_effects)
            for b in bullets:
                if b:
                    self.player_bullets.append(b)

        for p in self.powerup_drops:
            p.update(dt)
        self.powerup_drops = [p for p in self.powerup_drops if p.alive]

        for p in self.powerup_effects:
            p.update(dt)
        self.powerup_effects = [p for p in self.powerup_effects if p.active]

        for b in self.player_bullets:
            b.update(dt)
        self.player_bullets = [b for b in self.player_bullets if b.alive]

        for b in self.enemy_bullets:
            b.update(dt)
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive]

        self.update_formation(dt)

        for e in self.enemies:
            e.update(dt)

        self.enemy_shoot_timer -= dt
        if self.enemy_shoot_timer <= 0 and self.enemies:
            self.enemy_shoot_timer = max(0.25, 0.9 - self.level * 0.05)
            shooter = random.choice(self.enemies)
            cx = shooter.x + shooter.WIDTH / 2
            cy = shooter.y + shooter.HEIGHT
            self.enemy_bullets.append(Bullet(cx, cy, 280, 0, shooter.fw["color"]))

        self.handle_collisions()

        for f in self.floaters:
            f.update(dt)
        self.floaters = [f for f in self.floaters if f.alive]

        # lose condition: an enemy reaches the player's line
        for e in self.enemies:
            if e.y + e.HEIGHT >= self.player.y:
                self.lose_life(full=True)
                break

        if not self.enemies:
            self.state = STATE_WAVE_CLEAR
            self.message_timer = 2.2
            self.flash_msg = random.choice(
                ["WAVE SIMPLIFIED", "FATIGUE REDUCED", "SWARM PATCHED OUT"]
            )

    def update_formation(self, dt):
        if not self.enemies:
            return
        min_x = min(e.x for e in self.enemies)
        max_x = max(e.x + e.WIDTH for e in self.enemies)

        step = self.formation_dx * dt
        will_min = min_x + step
        will_max = max_x + step

        drop = 0
        if will_max > WIDTH - 20 or will_min < 20:
            self.formation_dx *= -1
            self.formation_drop += self.ENEMY_DROP_RATE
            drop = self.ENEMY_DROP_RATE
            step = 0

        for e in self.enemies:
            e.base_x += step
            e.base_y += drop

    def handle_collisions(self):
        # player bullets vs enemies
        for b in self.player_bullets:
            if not b.alive:
                continue
            for e in self.enemies:
                if e.alive and b.rect.colliderect(e.rect):
                    e.alive = False
                    if b.pierce_shot:
                        b.pierce_shot = False
                    else:
                        b.alive = False
                    enemy_killed_sound.play()
                    self.score += 10 * self.level
                    self.floaters.append(
                        FloatingText(
                            e.x + e.WIDTH / 2, e.y, random.choice(JOKES), e.fw["color"]
                        )
                    )
                    drops_powerup = random.random() < POWERUP_DROP_CHANCE
                    if drops_powerup: 
                        self.powerup_drops.append(PowerUpDrop(e.base_x + e.WIDTH/2, e.base_y + e.HEIGHT/2))
                    break
        self.enemies = [e for e in self.enemies if e.alive]
        self.player_bullets = [b for b in self.player_bullets if b.alive]
        self.powerup_drops = [p for p in self.powerup_drops if p.alive]

        # enemy bullets vs player
        pr = self.player.rect
        for b in self.enemy_bullets:
            if b.alive and b.rect.colliderect(pr):
                b.alive = False
                shield = any(p.effect == "shield" for p in self.powerup_effects)
                if not shield and self.player.immunity <= 0:
                    self.lose_life()
                    player_damaged_sound.play()
        self.enemy_bullets = [b for b in self.enemy_bullets if b.alive]

        # powerup drop vs player
        for p in self.powerup_drops:
            if p.alive and p.rect.colliderect(pr):
                p.alive = False
                self.upsert_powerup_effect(p.power)
                powerup_sound.play()
                self.floaters.append(
                    FloatingText(
                        p.x + p.WIDTH / 2, p.y, p.power["effect"].replace("_", " "), p.power["color"]
                    )
                )
        self.powerup_drops = [p for p in self.powerup_drops if p.alive]

    def upsert_powerup_effect(self, new_power):
        if new_power["effect"] == "extra_life" and self.player.lives < 3:
            self.player.lives += 1
            return

        if new_power["effect"] == "enemy_pushback" and self.formation_drop >= self.ENEMY_DROP_RATE:
            if self.formation_drop >= self.ENEMY_DROP_RATE * 2:
                upward = self.ENEMY_DROP_RATE * 2
            else:
                upward = self.ENEMY_DROP_RATE
            for e in self.enemies:
                e.base_y -= upward
            return

        for e in self.powerup_effects:
            if e.effect == new_power["effect"]:
                e.timer = new_power["timer"]
                break
        else:
            self.powerup_effects.append(PowerUpEffect(new_power))

    def lose_life(self, full=False):
        self.player.lives -= 1
        self.player.hit_flash = 0.3
        self.player.immunity = 1.5
        if full:
            self.player.lives = 0
        if self.player.lives <= 0:
            self.state = STATE_GAME_OVER

    # -- draw --------------------------------------------------------
    def draw(self, surf):
        if self.state == STATE_MENU:
            self.draw_menu(surf)
            return

        for p in self.powerup_drops:
            p.draw(surf)
        for e in self.enemies:
            e.draw(surf)
        for b in self.player_bullets:
            b.draw(surf)
        for b in self.enemy_bullets:
            b.draw(surf)
        self.player.draw(surf, self.powerup_effects)
        for f in self.floaters:
            f.draw(surf)

        self.draw_hud(surf)

        if self.state == STATE_WAVE_CLEAR:
            self.draw_center_banner(surf, self.flash_msg, GOOD_COLOR)
        elif self.state == STATE_GAME_OVER:
            self.draw_game_over(surf)

    def draw_hud(self, surf):
        score_img = FONT_SMALL.render(f"SCORE {self.score}", True, TEXT_COLOR)
        surf.blit(score_img, (16, 14))

        level_img = FONT_SMALL.render(f"WAVE {self.level}", True, TEXT_COLOR)
        surf.blit(level_img, (WIDTH / 2 - level_img.get_width() / 2, 14))

        powerups_label = FONT_SMALL.render("POWERUPS", True, TEXT_COLOR)
        surf.blit(powerups_label, (WIDTH - 450, 14))
        current_x = WIDTH - 350
        padding = 8
        for i, e in enumerate(self.powerup_effects):
            e.draw(surf, current_x, 14)
            current_x += e.width + padding

        lives_label = FONT_SMALL.render("LIVES", True, TEXT_COLOR)
        surf.blit(lives_label, (WIDTH - 190, 14))
        for i in range(self.player.lives):
            tag = FONT_SMALL.render("</>", True, HTMX_COLOR)
            surf.blit(tag, (WIDTH - 120 + i * 32, 12))

    def draw_center_banner(self, surf, text, color):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 16, 120))
        surf.blit(overlay, (0, 0))
        img = FONT_BIG.render(text, True, color)
        surf.blit(img, (WIDTH / 2 - img.get_width() / 2, HEIGHT / 2 - 60))
        sub = FONT_SMALL.render("next wave incoming...", True, TEXT_COLOR)
        surf.blit(sub, (WIDTH / 2 - sub.get_width() / 2, HEIGHT / 2 + 10))

    def draw_game_over(self, surf):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((10, 10, 16, 170))
        surf.blit(overlay, (0, 0))
        title = FONT_BIG.render("FATIGUE WON THIS TIME", True, DANGER_COLOR)
        surf.blit(title, (WIDTH / 2 - title.get_width() / 2, HEIGHT / 2 - 90))
        score = FONT_MED.render(f"final score: {self.score}", True, TEXT_COLOR)
        surf.blit(score, (WIDTH / 2 - score.get_width() / 2, HEIGHT / 2 - 20))
        hint = FONT_SMALL.render("press R to retry  -  ESC to quit", True, TEXT_COLOR)
        surf.blit(hint, (WIDTH / 2 - hint.get_width() / 2, HEIGHT / 2 + 30))

    def draw_menu(self, surf):
        title = FONT_BIG.render("</> vs The JS Fatigue", True, HTMX_COLOR)
        surf.blit(title, (WIDTH / 2 - title.get_width() / 2, 130))

        sub = FONT_SMALL.render(
            "defend the simple web. shoot the fatigue before it lands.",
            True, TEXT_COLOR,
        )
        surf.blit(sub, (WIDTH / 2 - sub.get_width() / 2, 200))

        # little preview row of enemies
        preview_y = 270
        spacing = 70
        start_x = WIDTH / 2 - (len(FRAMEWORKS) * spacing) / 2 + spacing / 2
        for i, fw in enumerate(FRAMEWORKS):
            x = start_x + i * spacing
            r = pygame.Rect(int(x - 24), preview_y, 48, 36)
            pygame.draw.rect(surf, (24, 24, 34), r, border_radius=8)
            pygame.draw.rect(surf, fw["color"], r, width=2, border_radius=8)
            img = fw.get("image")
            surf.blit(img, (r.centerx - img.get_width() // 2, r.centery - img.get_height() // 2))

        controls = [
            "ARROWS / A D  -  move",
            "SPACE  -  shoot",
        ]
        for i, line in enumerate(controls):
            img = FONT_SMALL.render(line, True, TEXT_COLOR)
            surf.blit(img, (WIDTH / 2 - img.get_width() / 2, 360 + i * 28))

        pulse = (math.sin(pygame.time.get_ticks() / 250) + 1) / 2
        start_color = tuple(
            int(HTMX_COLOR[c] + (255 - HTMX_COLOR[c]) * pulse * 0.5) for c in range(3)
        )
        start = FONT_MED.render("PRESS SPACE TO START", True, start_color)
        surf.blit(start, (WIDTH / 2 - start.get_width() / 2, 440))


# ----------------------------------------------------------------------------
# Main loop
# ----------------------------------------------------------------------------


async def main():
    game = Game()
    running = True

    while running:
        dt = clock.tick(FPS) / 1000.0
        dt = min(dt, 0.05)

        just_pressed = set()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                just_pressed.add(event.key)
                if event.key == pygame.K_ESCAPE:
                    running = False

        keys = pygame.key.get_pressed()

        game.update(dt, keys, just_pressed)

        draw_background(dt)
        game.draw(screen)
        pygame.display.flip()
        await asyncio.sleep(0)


    pygame.quit()


if __name__ == "__main__":
    asyncio.run(main())