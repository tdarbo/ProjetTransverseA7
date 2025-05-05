from settings import *


class Player(pygame.sprite.Sprite):
    def __init__(self, color, position, radius=BALL_RADIUS, mass=BALL_MASS, name=""):
        super().__init__()
        self.color = color
        self.mass = mass
        self.position = Vector(position)
        self.velocity = Vector(0, 0)
        self.radius = radius
        self.name = name

        self.hide = False

        # Bonus part
        self.bonus = None

        # Création d'une Surface pour représenter le joueur
        self.image = pygame.Surface((2 * self.radius, 2 * self.radius), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=position)

    def get_velocity(self):
        return self.velocity.length()

    def update(self):
        self.rect.center = (int(self.position.x), int(self.position.y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def reset(self):
        self.mass = BALL_MASS
        self.position.x, self.position.y = 0, 0
        self.velocity.x, self.velocity.y = 0, 0
        self.radius = BALL_RADIUS
