from ui_text import Text
from settings import *


class BroadcastManager(Text):
    def __init__(self):
        """Gère les messages à l'écran."""
        # On utilise Text dans ui_text pour gérer l'affichage du broadcast_manager
        super().__init__(text="", pos=(WINDOW_WIDTH // 2, 20), font_size=15, color = (255,255,255) ,font_name=FONT_PATH, align="center")
        self.duration = 5
        self.begintimer = 0
        self.timeout = True

    def draw(self, screen):
        """Affiche le message si le timeout n'est pas écoulé."""
        if not self.timeout:
            # On draw le texte de l'objet Text (dans ui_text)
            # gestion du fond
            padding = 6  # arbitraire
            background_rect = self.rect.inflate(padding * 2 , padding * 2 )
            pygame.draw.rect(screen, (213, 85, 52), background_rect)
            pygame.draw.rect(screen, '#3F170D', background_rect, width=1)
            super().draw(screen)
            # vérifie le timer
            self.timer()

    def broadcast(self, message):
        """Définit un nouveau message à afficher avec minuterie."""
        # Comme BroadcastManager est un enfant de Text,
        # on peut accéder aux méthodes et aux propriétés de Text via le self de BroadcastManager
        # set_text est définie dans Text et permet de changer le texte affiché.
        self.set_text(message)
        self.begintimer = pygame.time.get_ticks()
        self.timeout = False
        self.set_position((WINDOW_WIDTH // 2, 20), align="midtop")

    def timer(self):
        """Vérifie si le temps d'affichage est écoulé."""
        if ((pygame.time.get_ticks() - self.begintimer) // 1000) > self.duration:
            self.timeout = True

    def set_duration(self, seconds):
        """Change la durée d'affichage du message."""
        self.duration = seconds
