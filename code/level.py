from bonus_manager import BonusSpeed, BonusType
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
                    self.cur_player.bonus.consume_bonus(self.cur_player, self.players)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self.on_mouse_down(event)
        elif event.type == pygame.MOUSEMOTION:
            self.on_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            self.handle_shot(event)

    def on_mouse_down(self, event):
        if self.shot_taken:
            return
        adjusted_pos = self.map.camera.getAbsoluteCoord(event.pos)
        if self.cur_player.rect.collidepoint(adjusted_pos):
            self.dragging = True
            self.drag_start = Vector(self.cur_player.rect.center)
            self.drag_current = Vector(adjusted_pos)

    def on_mouse_motion(self, event):
        if self.dragging:
            adjusted_pos = self.map.camera.getAbsoluteCoord(event.pos)
            self.drag_current = Vector(adjusted_pos)

    def handle_shot(self, event):
        if self.dragging:
            self.game.sound_manager.play_sound(SOUNDS["ball"])
            self.score_manager.add_points(self.cur_player, self.hole_index)

            adjusted_pos = self.map.camera.getAbsoluteCoord(event.pos)
            velocity_vector = (self.drag_start - adjusted_pos) * FORCE_MULTIPLIER
            self.engine.resolve_shot(self.cur_player, velocity_vector)

            self.dragging = False
            self.shot_taken = True
            self.drag_start = None
            self.drag_current = None

    def update(self, dt):
        if self.cur_player.finished:
            self.shot_taken = True

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
            if DEBUG_MODE: self.cur_player.bonus = BonusSpeed()

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
                self.centerOnPlayer(self.cur_player)
                return
            print("skipped turn")
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
