from settings import *
from engine import Engine

class Level:
    """Gestion de la map, des tours et des événements"""

    def __init__(self, map_tiles, players, score_manager):
        """
        Initialise le niveau

        :param map_tiles: Les tuiles de la carte.
        :param players: Les joueurs du niveau.
        :param score_manager: Le gestionnaire de score.
        """
        self.map_tiles = map_tiles
        self.players = players
        self.engine = Engine(self)
        self.score_manager = score_manager
        self.current_player_index = 0
        self.current_player = players[0]
        self.shot_taken = False  # Indique si le joueur actif a déjà joué

        # Variables pour le drag & drop
        self.dragging = False
        self.drag_start = None # Vector
        self.drag_current = None # Vector
        self.force_multiplier = FORCE_MULTIPLIER

    def process_event(self, event):
        """
        Traite les événements pygame.

        :param event: L'événement pygame à traiter.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.on_mouse_down(event)
        elif event.type == pygame.MOUSEMOTION:
            self.on_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.on_mouse_up(event)

    def on_mouse_down(self, event):
        """
        Gère l'événement associé au clic.
        """
        # Empêche le drag & drop si le coup a déjà été joué
        if self.shot_taken:
            return
        # Vérifie si le clic est sur la balle du joueur
        if self.current_player.rect.collidepoint(event.pos):
            self.dragging = True
            # Fixe le point de départ au centre de la balle
            self.drag_start = Vector(self.current_player.rect.center)
            self.drag_current = Vector(event.pos)

    def on_mouse_motion(self, event):
        """
        Gère l'événement de mouvement de la souris.
        """
        if self.dragging:
            self.drag_current = Vector(event.pos)

    def on_mouse_up(self, event):
        """
        Gère l'événement associé au relâchement du clic de souris.
        """
        if self.dragging:
            pos = Vector(event.pos)
            # Calcul de la force à appliquer : différence entre le centre de la balle et le point relâché
            force = (self.drag_start - pos) * self.force_multiplier
            self.current_player.velocity += force
            self.dragging = False
            self.shot_taken = True
            self.drag_start = None
            self.drag_current = None

    def update(self, dt):
        """
        Met à jour l'état du niveau en fonction du temps écoulé.

        :param dt: Le temps écoulé depuis la dernière mise à jour.
        """
        self.engine.update(dt)
        for player in self.players:
            player.update()
        self.check_turn_end()

    def check_turn_end(self):
        """
        Vérifie si le tour du joueur est terminé et passe au joueur suivant si nécessaire.
        """
        if self.shot_taken and self.current_player.velocity.length() < VELOCITY_THRESHOLD:
            self.next_turn()

    def next_turn(self):
        """
        Passe au tour du joueur suivant.
        """
        self.shot_taken = False
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.current_player = self.players[self.current_player_index]
        print(f"Tour du joueur {self.current_player_index + 1}")

    def draw(self, screen):
        """
        Dessine le niveau sur l'écran.

        :param screen: La surface sur laquelle dessiner.
        """
        for tile in self.map_tiles:
            tile.draw(screen)
        for player in self.players:
            player.draw(screen)
        # Indique le joueur qui doit jouer avec un cercle blanc
        if not self.shot_taken:
            pygame.draw.circle(screen, pygame.Color("white"), self.current_player.rect.center, self.current_player.radius + 5, 2)
        # Affiche la ligne de visée
        if self.dragging and self.drag_start and self.drag_current:
            pygame.draw.line(screen, pygame.Color("black"), self.drag_start, self.drag_current, 3)
