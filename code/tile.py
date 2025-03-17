from settings import *

class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_id, x, y, width, height, color=None, image_path=None):
        super().__init__()
        self.id = tile_id

        if image_path is not None:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (width, height))
            except pygame.error as e:
                raise ValueError(f"Erreur lors du chargement de l'image: {image_path}. Détail: {e}")
        elif color is not None:
            self.image = pygame.Surface((width, height))
            if isinstance(color, str):
                color = pygame.Color(color)
            self.image.fill(color)
        else:
            raise ValueError("Vous devez fournir soit une couleur, soit un chemin d'image pour créer une Tile.")

        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        surface.blit(self.image, self.rect)