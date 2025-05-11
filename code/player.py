from settings import *
import time


# Class Player qui représente un joueur dans le jeu.
# Elle hérite de pygame.sprite.Sprite.
class Player(pygame.sprite.Sprite):
    def __init__(self, color, position, radius=BALL_RADIUS, mass=BALL_MASS, name=""):
        super().__init__()  # Initialise la classe Sprite
        self.color = color
        self.mass = mass
        self.position = Vector(position)
        self.velocity = Vector(0, 0)
        self.radius: int = radius  # Rayon du cercle représentant le joueur
        self.name: str = name

        self.finished = False  # Indique si le joueur a terminé le niveau/trajet

        self.bonus = None  # Contiendra un bonus actif (ou None s’il n’y en a pas)

        # Création de l’image représentant le joueur : un cercle de couleur dessiné
        self.image = pygame.Surface((2 * self.radius, 2 * self.radius), pygame.SRCALPHA)
        pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)
        self.rect = self.image.get_rect(center=position)

    def get_velocity(self):
        """Retourne la vitesse du joueur (norme du vecteur de vitesse)"""
        return self.velocity.length()

    def update(self):
        """Met à jour la position du sprite pour qu’elle suive la position logique du joueur"""
        self.rect.center = (int(self.position.x), int(self.position.y))

    def draw(self, surface):
        """Affiche le joueur sur la surface donnée, en tenant compte d’un éventuel effet de bonus"""
        if self.bonus is not None and self.bonus.name == "BonusFantome" and self.bonus.active:
            # Si le bonus "Fantôme" est actif, on dessine un cercle transparent
            transparent_color = (
            self.color[0], self.color[1], self.color[2], 100)  # Applique une transparence à la couleur
            pygame.draw.circle(self.image, transparent_color, (self.radius, self.radius), self.radius)
        else:
            # Sinon, dessine un cercle normal
            pygame.draw.circle(self.image, self.color, (self.radius, self.radius), self.radius)

        surface.blit(self.image, self.rect)

    def reset(self):
        """Réinitialise les paramètres du joueur (utile entre deux parties)"""
        self.finished = False  # Le joueur recommence, donc n’a pas fini
        self.mass = BALL_MASS  # Réinitialise la masse
        self.position.x, self.position.y = 0, 0  # Replace le joueur au point d’origine
        self.velocity.x, self.velocity.y = 0, 0  # Annule toute vitesse
        self.radius = BALL_RADIUS  # Réinitialise le rayon

    def update_gifs(self, overlay:pygame.Surface) -> None:
        """Gère l'affichage des effets spéciaux associés à un bonus actif (par ex. explosion visuelle)"""

        if self.bonus is None:
            return  # Si aucun bonus n’est actif, on ne fait rien

        if self.bonus.name == "BonusExplosion" and self.bonus.active:
            # Applique un flash blanc progressif dans le cas du bonus explosion
            # Si l’explosion vient juste d’être déclenchée, initialise les temps
            if self.bonus.start_time == -1:
                self.bonus.start_time = time.time()
                self.bonus.endtime = time.time() + 1  # L’effet dure 1 seconde

            current_alpha = 255  # Opacité maximale par défaut
            if time.time() < self.bonus.endtime:
                # Calcule la progression de l'effet pour diminuer l'opacité progressivement
                progress = time.time() - self.bonus.start_time
                current_alpha = int(255 * (1.0 - progress))
                if current_alpha < 0:
                    current_alpha = 0  # On évite les valeurs négatives
                overlay.fill((255, 255, 255, current_alpha))
            else:
                # L’effet est terminé, on désactive le bonus et on clear l'overlay
                self.bonus.active = False
                self.bonus.start_time = -1
                self.bonus.endtime = -1
                self.bonus = None
                overlay.fill((255, 255, 255, 0))
                return

        self.bonus.gif.update(overlay)
