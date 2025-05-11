from settings import *


class Text:
    def __init__(self, text, pos, font_size=16, color=(0, 0, 0), font_name=FONT_PATH, align="topleft"):
        """
        Initialise un objet texte à afficher.

        :param text: Texte à afficher
        :param pos: Position (x, y)
        :param font_size: Taille de la police
        :param color: Couleur du texte (tuple RGB)
        :param font_name: Chemin vers la police personnalisée
        :param align: Alignement du texte sur l'écran
        """
        self.text = text
        self.pos = pos
        self.color = color
        self.font = pygame.font.Font(font_name, font_size)  # Charge la police avec la taille donnée
        self.align = align

        self.rendered_text = self.font.render(self.text, True, self.color)
        self.rect = self.rendered_text.get_rect()
        self.set_position(self.pos, self.align)

    def draw(self, screen):
        """Affiche le texte à l'écran."""
        screen.blit(self.rendered_text, self.rect)

    def set_text(self, new_text):
        """Modifie le contenu du texte et le re-render."""
        self.text = new_text
        self.rendered_text = self.font.render(self.text, True, self.color)
        self.rect = self.rendered_text.get_rect()
        self.set_position(self.pos, self.align)

    def set_color(self, new_color):
        """Change la couleur du texte et le re-render."""
        self.color = new_color
        self.rendered_text = self.font.render(self.text, True, self.color)
        self.rect = self.rendered_text.get_rect()
        self.set_position(self.pos, self.align)

    def set_position(self, pos, align=None):
        """
        Met à jour la position du texte avec un nouvel alignement.

        :param pos: Nouvelle position (x, y)
        :param align: Alignement optionnel (centre, topleft, etc...)
        """
        # Vérifie que l'alignement est valide
        if align in {
            "topleft", "midtop", "topright", "midleft", "center",
            "midright", "bottomleft", "midbottom", "bottomright"
        }:
            self.align = align
        else:
            align = None  # Si invalide on ne le prend pas en compte

        self.pos = pos
        # On utilise "setattr" pour assigner dynamiquement un attribut comme rect.center ou rect.topleft
        # à une valeur (self.pos). On obtiendra donc rect.center = self.pos
        setattr(self.rect, self.align, self.pos)

    @property
    def width(self):
        """Retourne la largeur du texte."""
        return self.rect.width

    @property
    def height(self):
        """Retourne la hauteur du texte."""
        return self.rect.height
