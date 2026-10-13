class FloatingText:
    def __init__(self, x, y, text, color):
        self.x = x
        self.y = y
        self.text = text
        self.color = color
        self.life = 1.0

    @property
    def alive(self):
        return self.life > 0

    def update(self, dt):
        self.y -= 30 * dt
        self.life -= dt * 0.9

    def draw(self, surf, assets):
        img = assets.tiny.render(self.text, True, self.color)
        img.set_alpha(max(0, int(255 * self.life)))
        surf.blit(img, (self.x - img.get_width() / 2, self.y))
