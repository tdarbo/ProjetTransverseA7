
from camera import Camera
from settings import *
import pygame, pytmx

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_id, x, y, width, height, color=None, image_path=None, image_surface=None):
        super().__init__()
        self.id = tile_id

        if image_surface:
            self.image = pygame.transform.scale(image_surface, (width, height))
        elif image_path:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (width, height))
            except pygame.error as e:
                raise ValueError(f"Erreur lors du chargement de l'image: {image_path}. Détail: {e}")
        elif color:
            self.image = pygame.Surface((width, height))
            if isinstance(color, str):
                color = pygame.Color(color)
            self.image.fill(color)
        else:
            raise ValueError("Vous devez fournir une couleur, un chemin d'image ou une surface Pygame pour créer une Tile.")

        self.x, self.y = x, y
        self.rect = self.image.get_rect(topleft=(x, y))

    def is_on_screen(self, camera:Camera) -> bool:

        t_l, t_r, b_l, b_r = (self.x,self.y),(self.x+TILE_SIZE,self.y),(self.x,self.y+TILE_SIZE),(self.x+TILE_SIZE,self.y+TILE_SIZE)
        on_screen:bool = True

        if not camera.is_world_position_on_screen(t_l[0],t_l[1]) and not camera.is_world_position_on_screen(t_r[0],t_r[1]) and not camera.is_world_position_on_screen(b_l[0],b_l[1]) and not camera.is_world_position_on_screen(b_r[0],b_r[1]):
            on_screen = False

        return on_screen

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    def show(self, surface):
        surface.blit(self.image, self.rect)
