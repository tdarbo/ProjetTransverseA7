
from engine import Engine
from math import *
from settings import *


def norme(v):
    return hypot(v.x, v.y)

distance = Vector(0, 0)

class Level:
    """Gestion de la map, des tours et des événements"""

    def __init__(self, tiled_map, players, score_manager, screen_width=1280, screen_height=720):
        """Initialise le niveau."""
        self.map = tiled_map
        self.players = players
        self.engine = Engine(self)
        self.score_manager = score_manager
        self.current_player_index = 0
        self.current_player = players[0]
        self.shot_taken = False  # Indique si le joueur actif a joué

        # Variables pour le drag & drop
        self.dragging = False
        self.drag_start = None  # Vector
        self.drag_current = None  # Vector

        self.force_multiplier = FORCE_MULTIPLIER

        self.level_finished = False

        # Surfaces d'affichage
        self.overlay_surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self.map_size = (self.map.map_width, self.map.map_height)
        self.map_surf = pygame.Surface(self.map_size)

        self.map.teleportPlayersToSpawn(self.players)
        self.centerOnCurrentPlayer()

    def process_event(self, event):
        """Evénements pygame."""
        self.map.camera.process_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.centerOnCurrentPlayer()
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.on_mouse_down(event)
        elif event.type == pygame.MOUSEMOTION:
            self.on_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.on_mouse_up(event)

    def on_mouse_down(self, event):
        if self.shot_taken:
            return
        adjusted_pos = self.map.camera.getAbsoluteCoord(event.pos)
        if self.current_player.rect.collidepoint(adjusted_pos):
            self.dragging = True
            self.drag_start = Vector(self.current_player.rect.center)
            self.drag_current = Vector(adjusted_pos)

    def on_mouse_motion(self, event):
        global distance
        if self.dragging:
            adjusted_pos = self.map.camera.getAbsoluteCoord(event.pos)
            self.drag_current = Vector(adjusted_pos)
            distance = (self.drag_start - adjusted_pos) * self.force_multiplier

    def on_mouse_up(self, event):
        max = Vector(1000, 1000)
        if self.dragging:
            adjusted_pos = self.map.camera.getAbsoluteCoord(event.pos)
            force = (self.drag_start - adjusted_pos) * self.force_multiplier
            if norme(force) >= norme(max):
                force = force.normalize() * norme(max)
            self.current_player.velocity += force
            self.dragging = False
            self.shot_taken = True
            self.drag_start = None
            self.drag_current = None

    def update(self, dt):
        self.map.camera.animator.update()
        self.engine.update(dt)
        self.check_turn_end()

    def check_turn_end(self):
        """Vérifie si le tour est terminé et passe au joueur suivant."""
        if self.shot_taken:
            self.centerOnPlayers()
            if self.current_player.velocity.length() < VELOCITY_THRESHOLD:
                self.next_turn()

    def next_turn(self):
        """Passe au tour du joueur suivant."""
        self.shot_taken = False
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.current_player = self.players[self.current_player_index]
        print(f"Tour du joueur {self.current_player_index + 1}")
        self.centerOnCurrentPlayer()

    def draw_map(self, screen, players):
        zoom = self.map.camera.zoom_factor
        center = (screen.get_width() / 2, screen.get_height() / 2)
        # Réinitialise les surfaces
        self.overlay_surf.fill((0, 0, 0, 0))
        self.map_surf.fill("#BDDFFF")

        def world_to_screen(world_pos):
            return (
                center[0] - self.map.camera.offset_X * zoom + world_pos.x * zoom,
                center[1] - self.map.camera.offset_Y * zoom + world_pos.y * zoom
            )

        # Dessin des tuiles (on peut ignorer les tuiles de collision en mode normal)
        for tile in self.map.tiles:
            if tile.id == "Collision" and not DEBUG_MODE:
                continue
            tile.draw(self.map_surf)

        # Dessin des joueurs
        for player in self.players:
            player.draw(self.map_surf)

        # Cerclage du joueur actif s'il n'a pas encore joué
        if not self.shot_taken:
            pygame.draw.circle(
                surface=self.map_surf,
                color=pygame.Color("white"),
                center=self.current_player.rect.center,
                radius=self.current_player.radius + 5,
                width=2
            )

        # Dessin de la ligne de visé
        if self.dragging and self.drag_current is not None and round(norme(distance)) <= norme(Vector(200, 200)) :
            start_screen = world_to_screen(self.current_player.position)
            end_screen = world_to_screen(self.drag_current)
            pygame.draw.line(
                self.overlay_surf,
                pygame.Color("pink"),
                start_screen,
                end_screen,
                width=1
            )
        elif self.dragging and self.drag_start and self.drag_current and round(norme(distance)) <= norme(Vector(400, 400)):
            start_screen = world_to_screen(self.current_player.position)
            end_screen = world_to_screen(self.drag_current)
            pygame.draw.line(
                self.overlay_surf,
                pygame.Color("blue"),
                start_screen,
                end_screen,
                width=2
            )
        elif self.dragging and self.drag_start and self.drag_current and round(norme(distance)) <= norme(Vector(600, 600)):
            start_screen = world_to_screen(self.current_player.position)
            end_screen = world_to_screen(self.drag_current)
            pygame.draw.line(
                self.overlay_surf,
                pygame.Color("green"),
                start_screen,
                end_screen,
                width=3
            )
        elif self.dragging and self.drag_start and self.drag_current and round(norme(distance)) <= norme(Vector(800, 800)):
            start_screen = world_to_screen(self.current_player.position)
            end_screen = world_to_screen(self.drag_current)
            pygame.draw.line(
                self.overlay_surf,
                pygame.Color("yellow"),
                start_screen,
                end_screen,
                width=4
            )
        elif self.dragging and self.drag_start and self.drag_current and round(norme(distance)) <= norme(Vector(1000, 1000)):
            start_screen = world_to_screen(self.current_player.position)
            end_screen = world_to_screen(self.drag_current)
            pygame.draw.line(
                self.overlay_surf,
                pygame.Color("orange"),
                start_screen,
                end_screen,
                width=5
            )
        elif self.dragging and self.drag_start and self.drag_current and round(norme(distance)) > norme(Vector(1000, 1000)):
            start_screen = world_to_screen(self.current_player.position)
            end_screen = world_to_screen(self.drag_current)

            pygame.draw.line(
                self.overlay_surf,
                pygame.Color("red"),
                start_screen,
                end_screen,
                width=6
            )


        # Application du zoom sur la map
        resize_size = (int(self.map_size[0] * zoom), int(self.map_size[1] * zoom))
        map_surf_resized = pygame.transform.scale(self.map_surf, resize_size)

        m_x = center[0] - int(self.map.camera.offset_X * zoom)
        m_y = center[1] - int(self.map.camera.offset_Y * zoom)

        screen.blit(map_surf_resized, (m_x, m_y))
        screen.blit(self.overlay_surf, (0, 0))

    def draw(self, screen):
        """Dessine le niveau sur l'écran."""
        self.draw_map(screen, self.players)

    def centerOnCurrentPlayer(self):
        player = self.current_player
        x = player.position.x
        y = player.position.y

        camera = self.map.camera
        camera.animator.posToPosAndZoom(camera, (x, y), 1.0, 120)

    def centerOnPlayers(self):
        camera = self.map.camera
        x, y = 0, 0
        for player in self.players:
            x += player.position.x
            y += player.position.y

        p_count = len(self.players)
        x /= p_count
        y /= p_count

        camera.animator.posToPosAndZoom(camera, (x, y), 0.5, 15)
