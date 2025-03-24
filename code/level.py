from settings import *
from engine import Engine

class Level:
    """Gestion de la map, des tours et des événements"""

    def __init__(self, tiled_map, players, score_manager):
        """
        Initialise le niveau

        :param map_tiles: Les tuiles de la carte.
        :param players: Les joueurs du niveau.
        :param score_manager: Le gestionnaire de score.
        """
        self.map = tiled_map
        self.map_tiles = self.map.tiles
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
        Gère l'événement associé au clic, en prenant en compte l'offset et le zoom de la caméra.
        """
        if self.shot_taken:
            return

        # Correction : on applique l'inverse de l'offset ET du zoom correctement
        adjusted_pos = self.map.camera.getAbsoluteCoord(event.pos)

        print(f"🖱️ Position souris : {event.pos}")
        print(f"📐 Position ajustée : {adjusted_pos}")
        print(f"🎯 Position joueur : {self.current_player.rect.center}")
        print(f"📸 Offset : ({self.map.camera.offset_X}, {self.map.camera.offset_Y})")
        print(f"🔍 Zoom : {self.map.camera.zoom_factor}")

        # Vérifie si le clic est sur la balle du joueur
        if self.current_player.rect.collidepoint(adjusted_pos):
            self.dragging = True
            self.drag_start = Vector(self.current_player.rect.center)  # Centre réel de la balle
            self.drag_current = Vector(adjusted_pos)  # Point de départ ajusté

    def on_mouse_motion(self, event):
        """
        Gère l'événement de mouvement de la souris, ajusté pour la caméra.
        """
        if self.dragging:
            # Ajuste la position avec l'inverse de l'offset de la caméra
            adjusted_pos = self.map.camera.getAbsoluteCoord(event.pos)
            self.drag_current = Vector(adjusted_pos)

    def on_mouse_up(self, event):
        """
        Gère l'événement associé au relâchement du clic de souris, ajusté pour la caméra.
        """
        if self.dragging:
            # Ajuste la position avec l'inverse de l'offset de la caméra
            adjusted_pos = self.map.camera.getAbsoluteCoord(event.pos)
            pos = Vector(adjusted_pos)

            # Calcul de la force : différence entre le point de départ et le point relâché
            force = (self.drag_start - pos) * self.force_multiplier
            self.current_player.velocity += force

            # Réinitialise l'état de drag
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
        Dessine le niveau sur l'écran avec la gestion de la caméra.

        :param screen: La surface sur laquelle dessiner.
        """
        zoom = self.map.camera.zoom_factor

        # Centre de l'écran pour ajuster le zoom
        center_x = screen.get_width() / 2
        center_y = screen.get_height() / 2

        # Appliquer l'offset et le zoom à chaque tuile
        for tile in self.map_tiles:
            if tile.id == "Collision" and not DEBUG_MODE:
                continue

            # Appliquer le zoom aux dimensions
            zoomed_width = int(tile.rect.width * zoom)
            zoomed_height = int(tile.rect.height * zoom)

            # Calcul des nouvelles coordonnées centrées avec le zoom
            zoomed_x = center_x + (tile.rect.x - self.map.camera.offset_X - center_x) * zoom
            zoomed_y = center_y + (tile.rect.y - self.map.camera.offset_Y - center_y) * zoom

            # Redimensionner l'image
            zoomed_image = pygame.transform.scale(tile.image, (zoomed_width+1, zoomed_height+1))

            # Dessiner la tuile avec l'offset et le zoom
            screen.blit(zoomed_image, (zoomed_x+1, zoomed_y+1))

        # Appliquer l'offset et le zoom aux joueurs
        for player in self.players:
            zoomed_width = int(player.rect.width * zoom)
            zoomed_height = int(player.rect.height * zoom)

            zoomed_x = center_x + (player.rect.x - self.map.camera.offset_X - center_x) * zoom
            zoomed_y = center_y + (player.rect.y - self.map.camera.offset_Y - center_y) * zoom

            zoomed_image = pygame.transform.scale(player.image, (zoomed_width, zoomed_height))

            screen.blit(zoomed_image, (zoomed_x, zoomed_y))

        # Indique le joueur actif avec un cercle blanc
        if not self.shot_taken:
            player = self.current_player
            pygame.draw.circle(screen, pygame.Color("white"),
                               (center_x + (player.rect.centerx - self.map.camera.offset_X - center_x) * zoom,
                                center_y + (player.rect.centery - self.map.camera.offset_Y - center_y) * zoom),
                               int((player.radius + 5) * zoom), 2)

        # Affiche la ligne de visée
        if self.dragging and self.drag_start and self.drag_current:
            start_x = center_x + (self.drag_start[0] - self.map.camera.offset_X - center_x) * zoom
            start_y = center_y + (self.drag_start[1] - self.map.camera.offset_Y - center_y) * zoom

            current_x = center_x + (self.drag_current[0] - self.map.camera.offset_X - center_x) * zoom
            current_y = center_y + (self.drag_current[1] - self.map.camera.offset_Y - center_y) * zoom

            #pygame.draw.line(screen, pygame.Color("black"), (start_x, start_y),
            #                 (current_x, current_y), 3)


