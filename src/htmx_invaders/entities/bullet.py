import pygame

from ..settings import DANGER_COLOR, HEIGHT


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
