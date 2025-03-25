from settings import *


class Text:
    def __init__(self, text, pos, font_size=16, color=(0, 0, 0), font_name="../asset/font/font-regular-v2.ttf"):
        """
        Class pour gérer l'affichage du texte.

        :param text: Texte à afficher
        :param pos: Tuple (x, y) pour la position du texte
        :param font_size: Taille de la police
        :param color: Couleur du texte
        :param font_name: Nom de la police
        """
        self.text = text
        self.pos = pos
        self.color = color
        self.font = pygame.font.Font(font_name, font_size)
        self.rendered_text = self.font.render(self.text, True, self.color)
        self.rect = self.rendered_text.get_rect(topleft=self.pos)

    def draw(self, screen):
        """Affiche le texte sur l'écran."""
        screen.blit(self.rendered_text, self.rect)

    def update_text(self, new_text):
        """Met à jour le texte affiché."""
        self.text = new_text
        self.rendered_text = self.font.render(self.text, True, self.color)

    def set_color(self, new_color):
        """Change la couleur du texte."""
        self.color = new_color
        self.rendered_text = self.font.render(self.text, True, self.color)