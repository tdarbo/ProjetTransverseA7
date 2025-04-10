from settings import *

class BroadcastManager:
    def __init__(self):
        self.message = ''
        self.time = 5
        self.pos = (640 - len(self.message)*7,5)
        self.begintimer = 0
        self.timeout = False
        self.color = "white"
        self.font = pygame.font.Font(FONT_PATH, 15)
        self.rendered_text = self.font.render(self.message, True, self.color)
        self.rect = self.rendered_text.get_rect(topleft=self.pos)

    def draw(self, screen):
        """ Affiche le message et met à jour le timer."""
        if not(self.timeout):
            screen.blit(self.rendered_text, self.rect)
        BroadcastManager.timer(self)

    def broadcast(self,message):
        """ Lors de l'affichage d'un nouveau message cette fonction est appelée pour mettre à jour les données."""
        self.message = message
        self.pos=(640 - len(self.message)*7,5)
        self.rendered_text = self.font.render(self.message, True, self.color)
        self.rect = self.rendered_text.get_rect(topleft=self.pos)
        self.begintimer = pygame.time.get_ticks()
        self.timeout = False

    def change_time(self,time):
        """ Change le temps d'affichage du message, reglé par défaut à 5 secondes."""
        self.time=time

    def timer(self):
        """ Calcul le temps restant pour l'affichage du message et arête son afficage si le temps est écoulé."""
        if ((pygame.time.get_ticks() - self.begintimer) // 1000) > self.time :
            self.timeout = True

    def change_color(self,color):
        """ Pour changer la couleur des prochains messages si besoin, reglé par défaut à blanc."""
        self.color = color

