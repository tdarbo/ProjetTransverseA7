from bonus_manager import BonusSpeed, BonusType
import math
from time import sleep

import pygame

from bonus_manager import BonusSpeed, BonusType, BonusFantome, BonusAimant, BonusExplosion
from settings import *
from engine import Engine
from score import ScoreManager
from broadcast import BroadcastManager
from player import Player
from map import Map


class Level:
    """Gestion de la map, des tours et des événements"""

    def __init__(self, hole_index, tiled_map, players, score_manager, broadcast_manager, game):
        """Initialise le niveau."""
        self.game = game
        self.map: Map = tiled_map
        self.players: list[Player] = players
        self.engine: Engine = Engine(self)
        self.score_manager: ScoreManager = score_manager
        self.broadcast_manager: BroadcastManager = broadcast_manager
        self.cur_player_index: int = 0
        self.cur_player: Player = players[0]
        self.shot_taken: bool = False  # Indique si le joueur actif a joué
        self.hole_index = hole_index  # Numéro du trou associé au level

        # Variables pour le drag & drop
        self.dragging: bool = False
        self.drag_start: Vector = None
        self.drag_current: Vector = None

        self.finished: bool = False

        # Surfaces d'affichage
        self.map_size = (self.map.map_width, self.map.map_height)
        self.overlay_surf: pygame.surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)).convert_alpha()
        self.map_surf: pygame.surface = pygame.Surface(self.map_size).convert()

        # self.gif_manager.add_gif("../asset/GIF/Cactus.gif", 1511, 153, .5, True, False)
        self.bonus_gifs: list[str] = []
        self.debug_collisions = []
        self.debug_grid = False

        self.map.teleportPlayersToSpawn(self.players)
        self.centerOnPlayer(self.cur_player)

    def process_event(self, event):
        """Evénements pygame."""
        self.map.camera.process_event(event)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.centerOnPlayer(self.cur_player)
            elif event.key == pygame.K_h:
                self.cur_player.position.x = self.map.hole.x
                self.cur_player.position.y = self.map.hole.y
            elif event.key == pygame.K_e:
                if isinstance(self.cur_player.bonus, BonusType):
                    self.cur_player.bonus.consume_bonus(self.cur_player, self.players, self.overlay_surf)
            elif event.key == pygame.K_o:
                self.debug_grid = not self.debug_grid
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.on_mouse_down(event)
        elif event.type == pygame.MOUSEMOTION:
            self.on_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_shot(event)

    def on_mouse_down(self, event):
        if self.shot_taken:
            return
        adjusted_pos = self.map.camera.screen_to_world(event.pos)
        if self.cur_player.rect.collidepoint(adjusted_pos):
            self.dragging = True
            self.drag_start = Vector(self.cur_player.rect.center)
            self.drag_current = Vector(adjusted_pos)

    def on_mouse_motion(self, event):
        if self.dragging:
            adjusted_pos = self.map.camera.screen_to_world(event.pos)
            self.drag_current = Vector(adjusted_pos)

    def handle_shot(self, event):
        if self.dragging:
            self.game.sound_manager.play_sound(SOUNDS["ball"])
            self.score_manager.add_points(self.cur_player, self.hole_index)

            adjusted_pos = self.map.camera.screen_to_world(event.pos)
            velocity_vector = (self.drag_start - adjusted_pos) * FORCE_MULTIPLIER
            self.engine.resolve_shot(self.cur_player, velocity_vector)

            self.dragging = False
            self.shot_taken = True
            self.drag_start = None
            self.drag_current = None

    def update(self, dt):
        if self.cur_player.finished:
            self.shot_taken = True


        self.DEBUG_LOGS()
        self.update_bonuses()
        self.map.camera.animator.update()
        self.engine.update(dt)
        self.check_turn_end()

    def update_gifs(self):
        self.map.load_gif_bonuses(self.map_surf)
        self.cur_player.update_gifs(self.overlay_surf)

    def update_bonuses(self):
        for bonus in self.map.bonuses:
            bonus.update_bonus(self.map_surf)
        if isinstance(self.cur_player.bonus, BonusType):
            self.bonus_gifs.append(self.cur_player.bonus.icon_id)
        else:
             if DEBUG_MODE: self.cur_player.bonus = BonusExplosion()

    def check_turn_end(self):
        """Vérifie si le tour est terminé et passe au joueur suivant."""
        if self.shot_taken:
            self.centerOnPlayers(self.players)
            if self.cur_player.velocity.length() < VELOCITY_THRESHOLD:
                self.next_turn()

    def next_turn(self):
        """Passe au tour du joueur suivant."""
        self.shot_taken = False
        for i in range(len(self.players)):
            self.cur_player_index = (self.cur_player_index + 1) % len(self.players)
            self.cur_player = self.players[self.cur_player_index]
            if not self.cur_player.finished:
                self.broadcast_manager.broadcast(f"Tour du joueur {self.cur_player_index + 1}")
                print(f"Tour du joueur {self.cur_player_index + 1}")
                if isinstance(self.current_player.bonus, BonusFantome) or isinstance(self.current_player.bonus, BonusAimant):
                    self.current_player.bonus.next_turn(self.current_player)
                self.centerOnPlayer(self.cur_player)
                return
        # Aucun joueur actif
        self.finished = True

    def get_line_parameters(self, length: int) -> (str, int):
        width = 6
        color = "red"
        if length < 100:
            color = "pink"
            width = 1
        elif length < 200:
            color = "blue"
            width = 2
        elif length < 300:
            color = "green"
            width = 3
        elif length < 400:
            color = "yellow"
            width = 4
        elif length < 500:
            color = "orange"
            width = 5

        return color, width

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
        if not self.shot_taken and not self.cur_player.finished:
            pygame.draw.circle(
                surface=self.map_surf,
                color=pygame.Color("white"),
                center=self.cur_player.rect.center,
                radius=self.cur_player.radius + 5,
                width=2
            )

        # Dessin de la ligne de visé
        if self.dragging and self.drag_current is not None:
            line_length = int((self.drag_start - self.drag_current).length())
            line_color, line_width = self.get_line_parameters(line_length)
            pygame.draw.line(
                surface=self.overlay_surf,
                color=line_color,
                start_pos=self.world_to_screen_position(self.cur_player.position, center, zoom),
                end_pos=self.world_to_screen_position(self.drag_current, center, zoom),
                width=line_width
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
        self.render_physics_inspector(self.overlay_surf,self.map.camera,self.current_player)
        if self.debug_grid: self.render_tile_grid(self.overlay_surf,self.map.camera)
        screen.blit(self.overlay_surf, (0, 0))
        # print(self.map.camera.is_world_position_on_screen(self.cur_player.position.x, self.cur_player.position.y))

    def centerOnPlayer(self, player: Player):
        x = player.position.x
        y = player.position.y

        camera = self.map.camera
        camera.animator.posToPosAndZoom(camera, (x, y), 1.0, 120)

    def centerOnPlayers(self, players: list[Player]):
        camera = self.map.camera
        x, y = 0, 0
        for player in players:
            x += player.position.x
            y += player.position.y

        p_count = len(players)
        x /= p_count
        y /= p_count

        camera.animator.posToPosAndZoom(camera, (x, y), 0.5, 10)


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

    def render_physics_inspector(self, screen, camera, selected_player=None):
        """Displays detailed physics information for selected objects"""
        if not DEBUG_MODE:
            return

        # Default to first player if none selected
        if selected_player is None and self.players:
            selected_player = self.players[0]

        if selected_player:
            # Create background panel
            panel_width, panel_height = 300, 220
            panel_surf = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
            panel_surf.fill((0, 0, 0, 180))

            # Render physics data
            font = pygame.font.Font(None, 24)

            # Player basic info
            texts = [
                f"Object: {selected_player.name}",
                f"Position: ({selected_player.position.x:.1f}, {selected_player.position.y:.1f})",
                f"Velocity: ({selected_player.velocity.x:.2f}, {selected_player.velocity.y:.2f})",
                f"Speed: {selected_player.velocity.length():.2f}",
                f"Direction: {math.degrees(math.atan2(selected_player.velocity.y, selected_player.velocity.x)):.1f}°",
            ]

            # Add bonus info if present
            if hasattr(selected_player, 'bonus') and selected_player.bonus:
                texts.append(f"Bonus: {selected_player.bonus.__class__.__name__}")

            # Render each text line
            y_offset = 10
            for text in texts:
                text_surf = font.render(text, True, (255, 255, 255))
                panel_surf.blit(text_surf, (10, y_offset))
                y_offset += 28

            # Position panel in top-right corner
            screen.blit(panel_surf, (screen.get_width() - panel_width - 10, 10))

    def render_tile_grid(self, screen, camera):
        """Shows the tile grid with tile IDs for debugging map issues"""
        if not DEBUG_MODE:
            return

        # Only render tiles that are visible
        for tile in self.map.tiles:
            if camera.is_world_position_on_screen(tile.rect.centerx, tile.rect.centery):
                # Convert to screen coordinates
                screen_rect = pygame.Rect(
                    *camera.world_to_screen(tile.rect.left, tile.rect.top),
                    tile.rect.width * camera.zoom_factor,
                    tile.rect.height * camera.zoom_factor
                )

                # Draw tile outline
                color = (255, 0, 0) if tile.id == "Collision" else (
                    (0, 0, 255) if tile.id == "Water" else
                    (0, 255, 0) if tile.id == "Grass" else (100, 100, 100))

                pygame.draw.rect(screen, color, screen_rect, 1)

                # Render tile ID for debugging - only when zoomed in enough
                if camera.zoom_factor > 0.7:
                    font = pygame.font.Font(None, 18)
                    text = font.render(tile.id, True, (255, 255, 255))
                    text_rect = text.get_rect(center=screen_rect.center)

                    # Add semi-transparent background for text
                    bg_rect = text_rect.inflate(4, 4)
                    bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
                    bg_surf.fill((0, 0, 0, 128))
                    screen.blit(bg_surf, bg_rect)

                    screen.blit(text, text_rect)