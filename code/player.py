from settings import *
import time



class Player(pygame.sprite.Sprite):
    def __init__(self, color, position, radius=BALL_RADIUS, mass=BALL_MASS, name=""):
        super().__init__()
        self.color = color
        self.mass = mass
        self.position = Vector(position)
        self.velocity = Vector(0, 0)
        self.radius:int = radius
        self.name:str = name

        self.finished = False

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
        if self.bonus is not None and self.bonus.name == "BonusFantome" and self.bonus.active:
            # Draw a transparent circle for the ghost bonus
            transparent_color = (*self.color[:3], 100)  # Adjust alpha to make it less opaque
            pygame.draw.circle(self.image, transparent_color, (self.radius, self.radius), self.radius)
        else:
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)

        surface.blit(self.image, self.rect)

    def reset(self):
        self.mass = BALL_MASS
        self.position.x, self.position.y = 0, 0
        self.velocity.x, self.velocity.y = 0, 0
        self.radius = BALL_RADIUS

    def update_gifs(self, overlay:pygame.Surface) -> None:

        if self.bonus is None:
            return

        if self.bonus.name == "BonusExplosion" and self.bonus.active:
            current_alpha = 255
            if self.bonus.start_time == -1:
                self.bonus.start_time = time.time()
                self.bonus.endtime = time.time() + 1
            if time.time() < self.bonus.endtime:
                progress = (time.time() - self.bonus.start_time) / (1000 / 1000.0)
                current_alpha = int(255 * (1.0 - progress))
                if current_alpha < 0:
                    current_alpha = 0
                overlay.fill((255, 255, 255, current_alpha))
            else:
                self.bonus.active = False
                self.bonus.start_time = -1
                self.bonus.endtime = -1
                self.bonus = None
                overlay.fill((255, 255, 255, 0))
                return



        self.bonus.gif.update(overlay)
