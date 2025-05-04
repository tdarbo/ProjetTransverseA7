from settings import *


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type_id, x, y, width, height, image_surface):
        super().__init__()

        # Identifiant du type de la tuile
        # Ex : "Sand", "Grass", "Water", ...
        self.id = tile_type_id

        # Surface de l'image associée à la tuile
        self.image = image_surface

        # On initialise la position de la tuile
        # get_rect() est utilisée pour obtenir un rectangle représentant la position et la taille de l'image
        # Le rectangle est positionné en haut à gauche aux coordonnées (x, y)
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface):
        # Permet de dessiner la tuile sur une surface donnée
        # blit() est utilisée pour copier le contenu de l'image sur la surface aux coordonnées spécifiées par le rectangle
        surface.blit(self.image, self.rect)

    @property
    def x(self):
        return self.rect.x

    @property
    def y(self):
        return self.rect.y

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height
