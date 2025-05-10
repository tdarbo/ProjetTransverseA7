from settings import *


class Text:
    def __init__(self, text, pos, font_size=16, color=(0, 0, 0), font_name=FONT_PATH, align="topleft"):
        """
        Classe pour gérer l'affichage de texte.

        :param text: Texte à afficher
        :param pos: Position (x, y)
        :param font_size: Taille de la police
        :param color: Couleur du texte
        :param font_name: Police utilisée
        :param align: Alignement ("topleft", "center", "midbottom", etc.)
        """
        self.text = text
        self.pos = pos
        self.color = color
        self.font = pygame.font.Font(font_name, font_size)
        self.align = align

        self.rendered_text = self.font.render(self.text, True, self.color)
        self.rect = self.rendered_text.get_rect()
        self.set_position(self.pos, self.align)

    def draw(self, screen):
        """Affiche le texte sur l'écran."""
        screen.blit(self.rendered_text, self.rect)

    def set_text(self, new_text):
        """Met à jour le texte affiché et réaligne le texte."""
        self.text = new_text
        self.rendered_text = self.font.render(self.text, True, self.color)
        self.rect = self.rendered_text.get_rect()
        self.set_position(self.pos, self.align)

    def set_color(self, new_color):
        """Change la couleur du texte et réaligne le texte."""
        self.color = new_color
        self.rendered_text = self.font.render(self.text, True, self.color)
        self.rect = self.rendered_text.get_rect()
        self.set_position(self.pos, self.align)

    def set_position(self, pos, align=None):
        """Met à jour la position du texte avec le nouvel alignement."""
        # On vérifie si le paramètre d'alignement est valide
        if align in {"topleft", "midtop", "topright", "midleft", "center", "midright", "bottomleft", "midbottom",
                     "bottomright"}:
            self.align = align
        else:
            align = None
        # On met à jour la position du texte
        self.pos = pos
        setattr(self.rect, self.align, self.pos)
        # setattr permet de définir dynamiquement la valeur d'un attribut d'un objet
        # Si self.align = "topleft" alors setattr vient mettre à jour self.rect.topleft à self.pos,
        # pour centrer l'élément par rapport au coin supérieur gauche

    @property
    def width(self):
        return self.rect.width

    @property
    def height(self):
        return self.rect.height
