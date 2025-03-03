from settings import *
import pygame

class Ball(pygame.sprite.Sprite):
    def __init__(self, color, position, radius=BALL_RADIUS, mass=BALL_MASS):
        super().__init__()
        self.color = color
        self.mass = mass
        self.position = Vector(position)
        self.velocity = Vector(0, 0)
        self.radius = radius

        self.rect = pygame.Rect(0, 0, 2 * self.radius, 2 * self.radius)
        self.rect.center = position

    def update(self):
        # Met à jour la position du rect en fonction de la position de la balle
        self.rect.center = (int(self.position.x), int(self.position.y))

    def draw(self, surface):
        # Dessine la balle comme un cercle sur la surface donnée
        pygame.draw.circle(surface, self.color, (int(self.position.x), int(self.position.y)), self.radius)
