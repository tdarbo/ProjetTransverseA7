from time import sleep

import pygame

from bonus_manager import BonusSpeed, BonusType, BonusFantome, BonusAimant, BonusExplosion
from settings import *
from engine import Engine
from broadcast import BroadcastManager


class Level:
    """Gestion de la map, des tours et des événements"""

    def __init__(self, hole_number, tiled_map, players, score_manager, broadcast_manager, screen_width=1280,
                 screen_height=720):
        """Initialise le niveau."""
        self.map = tiled_map
        self.players = players
        self.engine = Engine(self)
        self.score_manager = score_manager
        self.broadcast_manager = broadcast_manager
        self.current_player_index = 0
        self.current_player = players[0]
        self.shot_taken = False  # Indique si le joueur actif a joué
        self.hole_number = hole_number  # Numéro du trou associé au level

        # Variables pour le drag & drop
        self.dragging = False
        self.drag_start = None  # Vector
        self.drag_current = None  # Vector

        self.force_multiplier = FORCE_MULTIPLIER

        self.finished = False

        # Surfaces d'affichage
        self.map_size = (self.map.map_width, self.map.map_height)
        self.overlay_surf = pygame.Surface((screen_width, screen_height)).convert_alpha()
        self.map_surf = pygame.Surface(self.map_size).convert()

        # self.gif_manager.add_gif("../asset/GIF/Cactus.gif", 1511, 153, .5, True, False)
        self.bonus_gifs = []
        self.debug_collisions = []

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
            elif event.key == pygame.K_e:
                if isinstance(self.current_player.bonus, BonusType):
                    self.current_player.bonus.consume_bonus(self.current_player, self.players, self.overlay_surf)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.on_mouse_down(event)
        elif event.type == pygame.MOUSEMOTION:
            self.on_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.on_mouse_up(event)

    def on_mouse_down(self, event):
        if self.shot_taken:
            return
        adjusted_pos = self.map.camera.screen_to_world(event.pos)
        if self.current_player.rect.collidepoint(adjusted_pos):
            self.dragging = True
            self.drag_start = Vector(self.current_player.rect.center)
            self.drag_current = Vector(adjusted_pos)

    def on_mouse_motion(self, event):
        if self.dragging:
            adjusted_pos = self.map.camera.screen_to_world(event.pos)
            self.drag_current = Vector(adjusted_pos)

    def on_mouse_up(self, event):
        if self.dragging:
            # On modifie le score du joueur
            # Il vient de jouer donc on lui ajoute 1 point
            self.score_manager.add_points(self.current_player, self.hole_number)

            if isinstance(self.current_player.bonus, BonusSpeed):
                self.current_player.bonus.consume_bonus(self.current_player, self.players)

            adjusted_pos = self.map.camera.screen_to_world(event.pos)
            new_velocity = (self.drag_start - adjusted_pos) * self.force_multiplier
            # if self.current_player.speed_bonus:
            #    new_velocity *= 2
            #    new_velocity = min(new_velocity, MAX_PLAYER_VELOCITY.length()*1.5)
            if new_velocity.length() >= MAX_PLAYER_VELOCITY.length():
                new_velocity = new_velocity.normalize() * MAX_PLAYER_VELOCITY.length()

            self.current_player.velocity += new_velocity
            self.dragging = False
            self.shot_taken = True
            self.drag_start = None
            self.drag_current = None

    def update(self, dt):
        if self.current_player.finished:
            self.shot_taken = True


        self.DEBUG_LOGS()
        self.update_bonuses()
        self.map.camera.animator.update()
        self.engine.update(dt)
        self.check_turn_end()

    def update_gifs(self):
        self.map.load_gif_bonuses(self.map_surf)


    def update_bonuses(self):
        for bonus in self.map.bonuses:
            bonus.update_bonus(self.map_surf)
        if isinstance(self.current_player.bonus, BonusType):
            self.bonus_gifs.append(self.current_player.bonus.icon_id)
        else:
             if DEBUG_MODE: self.current_player.bonus = BonusExplosion()


    def check_turn_end(self):
        """Vérifie si le tour est terminé et passe au joueur suivant."""
        if self.shot_taken:
            self.centerOnPlayers()
            if self.current_player.velocity.length() < VELOCITY_THRESHOLD:
                self.next_turn()

    def next_turn(self):
        """Passe au tour du joueur suivant."""
        self.shot_taken = False
        for i in range(len(self.players)):
            self.current_player_index = (self.current_player_index + 1) % len(self.players)
            self.current_player = self.players[self.current_player_index]
            if not self.current_player.finished:
                self.broadcast_manager.broadcast(f"Tour du joueur {self.current_player_index + 1}")
                print(f"Tour du joueur {self.current_player_index + 1}")
                if isinstance(self.current_player.bonus, BonusFantome) or isinstance(self.current_player.bonus, BonusAimant):
                    self.current_player.bonus.next_turn(self.current_player)
                self.centerOnCurrentPlayer()
                return
        # Aucun joueur actif
        self.finished = True

    def get_line_color(self, line_length: int) -> str:
        global width_line
        if line_length < 100:
            color = "pink"
            width_line = 1
        elif line_length < 200:
            color = "blue"
            width_line = 2
        elif line_length < 300:
            color = "green"
            width_line = 3
        elif line_length < 400:
            color = "yellow"
            width_line = 4
        elif line_length < 500:
            color = "orange"
            width_line = 5
        else:
            color = "red"
            width_line = 6
        return color

    def world_to_screen_position(self, world_pos, center_point, camera_zoom):
        return (
            center_point[0] - self.map.camera.offset_X * camera_zoom + world_pos.x * camera_zoom,
            center_point[1] - self.map.camera.offset_Y * camera_zoom + world_pos.y * camera_zoom
        )

    def draw_map(self, screen):
        zoom = self.map.camera.zoom_factor
        center = (screen.get_width() / 2, screen.get_height() / 2)
        # Réinitialise les surfaces
        self.map_surf.fill("#BDDFFF")
        self.overlay_surf.fill((0, 0, 0, 0))

        for tile in self.map.tiles:
            if tile.id in {"Collision", "Bounce"} and not DEBUG_MODE:
                continue
            tile.draw(self.map_surf)

        pygame.draw.circle(
            surface=self.map_surf,
            color=pygame.Color("black"),
            center=(self.map.hole.x, self.map.hole.y),
            radius=20
        )

        self.map.load_gif_bonuses(self.map_surf)


        for bonus in self.map.bonuses:
            bonus.draw_bonus(self.map_surf)

        # Dessin des joueurs
        for player in self.players:
            if not player.finished:
                player.draw(self.map_surf)

        # Cerclage du joueur actif s'il n'a pas encore joué
        if not self.shot_taken and not self.current_player.finished:
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
                width=width_line
            )

        resize_size = (int(self.map_size[0] * zoom), int(self.map_size[1] * zoom))
        if zoom == 1.0:
            map_surf_resized = self.map_surf
        else:
            map_surf_resized = pygame.transform.scale(self.map_surf, resize_size)
        zoom_offset_x = int(self.map.camera.offset_X * zoom)
        zoom_offset_y = int(self.map.camera.offset_Y * zoom)
        m_x = center[0] - zoom_offset_x
        m_y = center[1] - zoom_offset_y
        screen.blit(map_surf_resized, (m_x, m_y))

    def draw(self, screen):
        """Dessine le niveau sur l'écran."""
        self.draw_map(screen)
        self.score_manager.draw(self.overlay_surf)
        self.broadcast_manager.draw(self.overlay_surf)
        self.current_player.update_gifs(self.overlay_surf)
        self.render_debug_info(self.overlay_surf,self.map.camera)
        screen.blit(self.overlay_surf, (0, 0))
        # print(self.map.camera.is_world_position_on_screen(self.current_player.position.x, self.current_player.position.y))

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


    def DEBUG_LOGS(self):
        if DEBUG_MODE:
            pass#if isinstance(self.current_player.bonus, BonusFantome): print(self.current_player.bonus)

    def render_debug_info(self, screen, camera):
        """
        Renders debug information when DEBUG_MODE is enabled.
        Accounts for camera position and zoom.
        """
        if not DEBUG_MODE:
            return

        # Draw debug info for all players
        for player in self.players:
            # Convert world position to screen position
            screen_pos_x, screen_pos_y = camera.world_to_screen(player.position.x, player.position.y)

            # Calculate velocity endpoint in screen space
            velocity_end_x, velocity_end_y = camera.world_to_screen(
                player.position.x + player.velocity.x,
                player.position.y + player.velocity.y
            )

            # Draw velocity vector (only if on screen)
            if (camera.is_position_on_screen(screen_pos_x, screen_pos_y) or
                    camera.is_position_on_screen(velocity_end_x, velocity_end_y)):
                pygame.draw.line(
                    screen,
                    (0, 255, 0),  # Green
                    (screen_pos_x, screen_pos_y),
                    (velocity_end_x, velocity_end_y),
                    2
                )

            # Draw player hitbox (converted to screen space)
            rect_screen = pygame.Rect(
                camera.world_to_screen(player.rect.left, player.rect.top),
                (player.rect.width * camera.zoom_factor, player.rect.height * camera.zoom_factor)
            )
            pygame.draw.rect(screen, (255, 0, 0), rect_screen, 1)

        # Draw collision debug info
        for collision in self.debug_collisions[:]:  # Use a copy of the list for safe removal
            # Calculate age of collision for fade effect
            age = pygame.time.get_ticks() - collision['time']
            if age > 3000:  # Remove collisions older than 3 seconds
                self.debug_collisions.remove(collision)
                continue

            # Fade based on age (255 to 0 over 3 seconds)
            alpha = 255 - int(age / 3000 * 255)

            pos = collision['position']
            normal = collision['normal']
            velocity = collision['velocity']

            # Convert position to screen coordinates
            screen_pos_x, screen_pos_y = camera.world_to_screen(pos.x, pos.y)

            # Calculate normal vector endpoint in screen space
            # Scale the length by zoom factor
            normal_length = 50 * camera.zoom_factor
            normal_end_x, normal_end_y = camera.world_to_screen(
                pos.x + normal.x * 50,
                pos.y + normal.y * 50
            )

            # Calculate velocity endpoint in screen space
            velocity_scale = min(1.0, velocity.length() / 10)  # Normalize velocity display
            velocity_end_x, velocity_end_y = camera.world_to_screen(
                pos.x + velocity.x * velocity_scale,
                pos.y + velocity.y * velocity_scale
            )

            # Only draw if at least part of the vectors are on screen
            if (camera.is_position_on_screen(screen_pos_x, screen_pos_y) or
                    camera.is_position_on_screen(normal_end_x, normal_end_y)):
                # Create surface with alpha for fade effect
                if pygame.version.vernum[0] >= 2:  # For pygame 2.0+
                    # Draw normal vector (red)
                    pygame.draw.line(
                        screen,
                        pygame.Color(255, 0, 0, alpha),  # Red with fade
                        (screen_pos_x, screen_pos_y),
                        (normal_end_x, normal_end_y),
                        2
                    )
                else:
                    # For older pygame versions that don't support alpha in color
                    line_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                    pygame.draw.line(
                        line_surf,
                        (255, 0, 0, alpha),  # Red with fade
                        (screen_pos_x, screen_pos_y),
                        (normal_end_x, normal_end_y),
                        2
                    )
                    screen.blit(line_surf, (0, 0))

            # Only draw if at least part of the vectors are on screen
            if (camera.is_position_on_screen(screen_pos_x, screen_pos_y) or
                    camera.is_position_on_screen(velocity_end_x, velocity_end_y)):
                # Create surface with alpha for fade effect
                if pygame.version.vernum[0] >= 2:  # For pygame 2.0+
                    # Draw resulting velocity (green)
                    pygame.draw.line(
                        screen,
                        pygame.Color(0, 255, 0, alpha),  # Green with fade
                        (screen_pos_x, screen_pos_y),
                        (velocity_end_x, velocity_end_y),
                        2
                    )
                else:
                    # For older pygame versions that don't support alpha in color
                    line_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
                    pygame.draw.line(
                        line_surf,
                        (0, 255, 0, alpha),  # Green with fade
                        (screen_pos_x, screen_pos_y),
                        (velocity_end_x, velocity_end_y),
                        2
                    )
                    screen.blit(line_surf, (0, 0))
