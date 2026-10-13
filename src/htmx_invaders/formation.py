"""The swarm of enemies: layout, marching and edge-bouncing."""

import random

from .content import FRAMEWORKS
from .entities import Enemy
from .settings import WIDTH


class Formation:
    DROP_STEP = 18      # px the swarm descends each time it hits a wall
    EDGE_MARGIN = 20
    SPACING_X = 64
    SPACING_Y = 58
    TOP = 70

    def __init__(self):
        self.enemies: list[Enemy] = []
        self.dx = 0.0          # px/sec horizontal drift
        self.total_drop = 0.0  # cumulative descent so far

    def __iter__(self):
        return iter(self.enemies)

    def __len__(self):
        return len(self.enemies)

    def spawn(self, level):
        rows = min(3 + (level - 1) // 2, 7)
        cols = min(6 + (level - 1), 16)
        total_w = cols * self.SPACING_X
        start_x = (WIDTH - total_w) / 2 + self.SPACING_X / 2 - Enemy.WIDTH / 2

        self.enemies = []
        for row in range(rows):
            for col in range(cols):
                e = Enemy(col, row, random.choice(FRAMEWORKS))
                e.base_x = start_x + col * self.SPACING_X
                e.base_y = self.TOP + row * self.SPACING_Y
                self.enemies.append(e)

        self.dx = 50.0 + level * 8.0
        self.total_drop = 0.0

    def update(self, dt):
        if not self.enemies:
            return
        min_x = min(e.x for e in self.enemies)
        max_x = max(e.x + e.WIDTH for e in self.enemies)

        step = self.dx * dt
        drop = 0
        if max_x + step > WIDTH - self.EDGE_MARGIN or min_x + step < self.EDGE_MARGIN:
            self.dx *= -1
            self.total_drop += self.DROP_STEP
            drop = self.DROP_STEP
            step = 0

        for e in self.enemies:
            e.base_x += step
            e.base_y += drop
            e.update(dt)

    def push_back(self):
        """Shove the swarm back up. Returns False if it hasn't descended yet."""
        if self.total_drop < self.DROP_STEP:
            return False
        upward = self.DROP_STEP * 2 if self.total_drop >= self.DROP_STEP * 2 else self.DROP_STEP
        for e in self.enemies:
            e.base_y -= upward
        return True

    def remove_dead(self):
        self.enemies = [e for e in self.enemies if e.alive]

    def reached(self, line_y):
        """True if any enemy has descended to `line_y`."""
        return any(e.y + e.HEIGHT >= line_y for e in self.enemies)
