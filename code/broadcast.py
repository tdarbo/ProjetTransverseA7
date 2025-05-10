import pygame

from ui_text import Text
from settings import *


class BroadcastManager:
    def __init__(self):
        """Gère les messages à l'écran."""
        # On utilise Text dans ui_text pour gérer l'affichage du broadcast_manager
        self.text = Text(
            text="",
            pos=(
                WINDOW_WIDTH // 2,
                OVERLAY_MENU_MARGIN + OVERLAY_MENU_PADDING + 6
            ),
            font_size=12,
            color=(255, 255, 255),
            align="center"
        )
        self.duration = 15
        self.begintimer = 0
        self.timeout = True

    def draw(self, screen):
        """Affiche le message si le timeout n'est pas écoulé."""
        if not self.timeout:
            # On draw le texte de l'objet Text (dans ui_text)
            # gestion du fond
            bg_rect = pygame.Rect(
                self.text.rect.x - OVERLAY_MENU_PADDING,
                self.text.rect.y - OVERLAY_MENU_PADDING,
                self.text.width + 2 * OVERLAY_MENU_PADDING,
                self.text.height + 2 * OVERLAY_MENU_PADDING - 6
            )
            pygame.draw.rect(screen, (213, 85, 52), bg_rect)
            pygame.draw.rect(screen, '#3F170D', bg_rect, width=3)
            self.text.draw(screen)
            # Vérifie le timer
            self.timer()

    def broadcast(self, message):
        """Définit un nouveau message à afficher avec minuterie."""
        # Comme BroadcastManager est un enfant de Text,
        # on peut accéder aux méthodes et aux propriétés de Text via le self de BroadcastManager
        # set_text est définie dans Text et permet de changer le texte affiché.
        self.text.set_text(message)
        self.timeout = False
        self.begintimer = pygame.time.get_ticks()

    def timer(self):
        """Vérifie si le temps d'affichage est écoulé."""
        if ((pygame.time.get_ticks() - self.begintimer) // 1000) > self.duration:
            self.timeout = True

    def set_duration(self, seconds):
        """Change la durée d'affichage du message."""
        self.duration = seconds
