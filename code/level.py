from time import sleep

import pygame

from gif_manager import GifManager
from settings import *
from engine import Engine
from broadcast import BroadcastManager


class Level:
    """Gestion de la map, des tours et des événements"""

    def __init__(self, hole_number, tiled_map, players, score_manager, screen_width=1280, screen_height=720):
        """Initialise le niveau."""
        self.map = tiled_map
        self.players = players
        self.engine = Engine(self)
        self.score_manager = score_manager
        self.broadcast_manager = BroadcastManager()
        self.current_player_index = 0
        self.current_player = players[0]
        self.shot_taken = False  # Indique si le joueur actif a joué
        self.hole_number = hole_number # Numéro du trou associé au level

        # Variables pour le drag & drop
        self.dragging = False
        self.drag_start = None  # Vector
        self.drag_current = None  # Vector

        self.force_multiplier = FORCE_MULTIPLIER

        self.finished = False

        # Surfaces d'affichage
        self.overlay_surf = pygame.Surface((screen_width, screen_height), pygame.SRCALPHA)
        self.map_size = (self.map.map_width, self.map.map_height)
        self.map_surf = pygame.Surface(self.map_size)

        self.gif_manager = GifManager()

        self.gif_manager.add_gif("../asset/GIF/Balle.gif",self.map.hole.x,self.map.hole.y,True, False)

        self.map.teleportPlayersToSpawn(self.players)
        self.centerOnCurrentPlayer()

    def process_event(self, event):
        """Evénements pygame."""
        self.map.camera.process_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.centerOnCurrentPlayer()
            elif event.key == pygame.K_h:
                self.current_player.position.x = self.map.hole.x
                self.current_player.position.y = self.map.hole.y
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
        if self.dragging:
            adjusted_pos = self.map.camera.getAbsoluteCoord(event.pos)
            self.drag_current = Vector(adjusted_pos)

    def on_mouse_up(self, event):
        if self.dragging:
            # On modifie le score du joueur
            # Il vient de jouer donc on lui ajoute 1 point
            self.score_manager.add_points(self.current_player, self.hole_number)

            adjusted_pos = self.map.camera.getAbsoluteCoord(event.pos)
            new_velocity = (self.drag_start - adjusted_pos) * self.force_multiplier
            if new_velocity.length() >= MAX_PLAYER_VELOCITY.length():
                new_velocity = new_velocity.normalize() * MAX_PLAYER_VELOCITY.length()

            self.current_player.velocity += new_velocity
            self.dragging = False
            self.shot_taken = True
            self.drag_start = None
            self.drag_current = None

    def update(self, dt):
        if self.current_player.hide:
            self.shot_taken = True

        if self.finished:
            print("Level finished")

        self.map.camera.animator.update()
        self.engine.update(dt)
        self.check_turn_end()

    def check_turn_end(self):
        """Vérifie si le tour est terminé et passe au joueur suivant."""
        if self.shot_taken:
            self.centerOnPlayers()
            if self.current_player.velocity.length() < VELOCITY_THRESHOLD:
                self.next_turn()

    def next_turn(self, i = 0):
        """Passe au tour du joueur suivant."""
        l = i
        self.shot_taken = False
        if l > len(self.players):
            self.finished = True
            return

        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.current_player = self.players[self.current_player_index]
        if self.current_player.hide:
            self.next_turn(l+1)
            print("skipped turn")
        else:
            print(f"Tour du joueur {self.current_player_index + 1}")
            self.centerOnCurrentPlayer()

    def world_to_screen_position(self, world_pos, center_point, camera_zoom):
        return (
            center_point[0] - self.map.camera.offset_X * camera_zoom + world_pos.x * camera_zoom,
            center_point[1] - self.map.camera.offset_Y * camera_zoom + world_pos.y * camera_zoom
        )

    def get_line_color(self, line_length: int) -> str:
        global width_line
        if line_length < 100 :
            color = "pink"
            width_line = 1
        elif line_length < 200 :
            color = "blue"
            width_line = 2
        elif line_length < 300 :
            color = "green"
            width_line = 3
        elif line_length < 400 :
            color = "yellow"
            width_line = 4
        elif line_length < 500 :
            color = "orange"
            width_line = 5
        else :
            color = "red"
            width_line = 6
        return color

    def draw_map(self, screen):
        zoom = self.map.camera.zoom_factor
        center = (screen.get_width() / 2, screen.get_height() / 2)
        # Réinitialise les surfaces
        self.overlay_surf.fill((0, 0, 0, 0))
        self.map_surf.fill("#BDDFFF")

        # Dessin des tuiles (on peut ignorer les tuiles de collision en mode normal)
        for tile in self.map.tiles:
            if tile.id == "Collision" and not DEBUG_MODE:
                continue
            tile.draw(self.map_surf)

        pygame.draw.circle(
            surface=self.map_surf,
            color=pygame.Color("black"),
            center=(self.map.hole.x, self.map.hole.y),
            radius=20
        )

        # Dessin des joueurs
        for player in self.players:
            if not player.hide:
                player.draw(self.map_surf)

        # Cerclage du joueur actif s'il n'a pas encore joué
        if not self.shot_taken and not self.current_player.hide:
            pygame.draw.circle(
                surface=self.map_surf,
                color=pygame.Color("white"),
                center=self.current_player.rect.center,
                radius=self.current_player.radius + 5,
                width=2
            )

        # Dessin de la ligne de visé
        if self.dragging and self.drag_current is not None:
            line_length = (self.current_player.position - self.drag_current).length()
            pygame.draw.line(
                self.overlay_surf,
                pygame.Color(self.get_line_color(line_length)),
                self.world_to_screen_position(self.current_player.position, center, zoom),
                self.world_to_screen_position(self.drag_current, center, zoom),
                width = width_line
                )

        # Application du zoom sur la map
        resize_size = (int(self.map_size[0] * zoom), int(self.map_size[1] * zoom))
        map_surf_resized = pygame.transform.scale(self.map_surf, resize_size)

        m_x = center[0] - int(self.map.camera.offset_X * zoom)
        m_y = center[1] - int(self.map.camera.offset_Y * zoom)

        screen.blit(map_surf_resized, (m_x, m_y))

    def draw(self, screen):
        """Dessine le niveau sur l'écran."""
        self.draw_map(screen)
        self.score_manager.draw(self.overlay_surf)
        self.broadcast_manager.draw(self.overlay_surf)
        self.gif_manager.update_all(self.map_surf,self.overlay_surf)
        screen.blit(self.overlay_surf, (0, 0))

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
