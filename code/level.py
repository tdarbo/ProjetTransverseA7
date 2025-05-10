from settings import *
from bonus_manager import BonusSpeed, BonusType
from engine import Engine
from score import ScoreManager
from broadcast import BroadcastManager
from player import Player
from map import Map


class Level:
    """Gestion de la map, des tours et des événements"""

    def __init__(self, hole_index, map_obj, players, score_manager, broadcast_manager, game):
        """Initialise le niveau."""
        self.game = game
        self.hole_index = hole_index  # Numéro du trou associé au niveau

        self.map: Map = map_obj
        self.players: list[Player] = players
        self.engine: Engine = Engine(self)
        self.score_manager: ScoreManager = score_manager
        self.broadcast_manager: BroadcastManager = broadcast_manager

        # Gestion des tours des joueurs
        self.cur_player_index: int = 0
        self.cur_player: Player = None
        self.shot_taken: bool = False  # Indique si le joueur actif a joué

        # Variables pour la ligne de visée
        self.dragging: bool = False
        self.drag_start: Vector = None
        self.drag_current: Vector = None

        # État du jeu
        self.finished: bool = False

        # Configuration des surfaces et des gifs
        self.map_size = (self.map.map_width, self.map.map_height)
        self.overlay_surf: pygame.surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT)).convert_alpha()
        self.map_surf: pygame.surface = pygame.Surface(self.map_size).convert()
        self.bonus_gifs: list[str] = []

        # Initialisation du niveau
        self.initialize_level()

    def initialize_level(self):
        """Initialise le niveau : place les joueurs et prépare le premier tour"""
        # Placement initial des joueurs
        self.map.teleportPlayersToSpawn(self.players)
        # Configuration du premier joueur
        self.setup_first_player()
        # Chargement des données visuelles
        self.load_graphics()

    def setup_first_player(self):
        """Configure le premier joueur et les variables associées"""
        self.cur_player_index: int = 0
        self.cur_player: Player = self.players[0]
        self.shot_taken: bool = False

        self.dragging: bool = False
        self.drag_start: Vector = None
        self.drag_current: Vector = None

        self.start_player_turn()

    def load_graphics(self):
        """Charge les ressources graphiques comme les GIFs"""
        # Chargement des GIFs des bonus
        self.map.load_gif_bonuses(self.map_surf)
        # self.gif_manager.add_gif("../asset/GIF/Cactus.gif", 1511, 153, .5, True, False)

    def process_event(self, event):
        """Gère les événements pygame."""
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
        # Si bouton gauche de la souris est enfoncé
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                self.on_mouse_down(event)
        elif event.type == pygame.MOUSEMOTION:
            self.on_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                self.handle_shot(event)

    def on_mouse_down(self, event):
        if not self.shot_taken:
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
            adjusted_pos = self.map.camera.getAbsoluteCoord(event.pos)
            velocity_vector = (self.drag_start - adjusted_pos) * FORCE_MULTIPLIER
            self.engine.resolve_shot(self.cur_player, velocity_vector)
            self.score_manager.add_points(self.cur_player, self.hole_index)

            self.dragging = False
            self.shot_taken = True
            self.drag_start = None
            self.drag_current = None

    def update(self, dt):
        """Met à jour l'état du niveau"""
        if self.cur_player.finished:
            self.shot_taken = True

        self.update_game_elements(dt)
        self.check_turn_end()

    def update_game_elements(self, dt):
        """Met à jour les différents éléments du jeu"""
        self.update_bonuses()
        self.map.camera.animator.update()
        self.engine.update(dt)

    def update_gifs(self):
        """Met à jour les animations GIF"""
        self.map.load_gif_bonuses(self.map_surf)
        self.cur_player.update_gifs(self.overlay_surf)

    def update_bonuses(self):
        """Met à jour les bonus"""
        for bonus in self.map.bonuses:
            bonus.update_bonus(self.map_surf)

        # Gestion des bonus du joueur actuel
        if isinstance(self.cur_player.bonus, BonusType):
            self.bonus_gifs.append(self.cur_player.bonus.icon_id)
        else:
            if DEBUG_MODE:
                self.cur_player.bonus = BonusSpeed()

    def check_turn_end(self):
        """Vérifie si le tour est terminé et passe au joueur suivant."""
        if self.shot_taken:
            self.centerOnPlayers(self.players)

            # Vérifier si tous les joueurs sont immobiles
            is_next_turn = True
            for player in self.players:
                if player.velocity.length() > VELOCITY_THRESHOLD:
                    is_next_turn = False
                    break
            if is_next_turn:
                self.next_turn()

    def next_turn(self):
        """Passe au tour du joueur suivant."""
        self.shot_taken = False

        # Recherche du prochain joueur actif
        for i in range(len(self.players)):
            self.cur_player_index = (self.cur_player_index + 1) % len(self.players)
            self.cur_player = self.players[self.cur_player_index]
            if not self.cur_player.finished:
                # Si le joueur trouvé n'a pas terminé, on démarre son tour
                self.start_player_turn()
                return

        # Si on arrive ici, c'est que tous les joueurs ont terminé
        self.finished = True

    def start_player_turn(self):
        """Démarre le tour d'un joueur"""
        # Annonce du tour du joueur
        self.broadcast_manager.broadcast(f"C'est à {self.cur_player.name} de jouer !")
        # Centre la caméra sur le joueur
        self.centerOnPlayer(self.cur_player)

    def get_line_parameters(self, length: int) -> (str, int):
        """Détermine les paramètres de la ligne de visée en fonction de sa longueur"""
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

    def world_to_screen_position(self, world_pos, center, zoom):
        """Convertit une position du monde en position d'écran"""
        return (
            center[0] - self.map.camera.offset_X * zoom + world_pos.x * zoom,
            center[1] - self.map.camera.offset_Y * zoom + world_pos.y * zoom
        )

    def draw_map(self, screen):
        """Dessine la carte et tous ses éléments"""
        zoom = self.map.camera.zoom_factor
        center = (screen.get_width() / 2, screen.get_height() / 2)

        # Réinitialise les surfaces
        self.map_surf.fill("#BDDFFF")
        self.overlay_surf.fill((0, 0, 0, 0))

        self.draw_map_elements()
        self.draw_players()
        self.draw_aiming_line(center, zoom)

        # Application du zoom et rendu final
        self.render_map_to_screen(screen, center, zoom)

    def draw_map_elements(self):
        """Dessine les éléments de la carte"""
        # Dessiner les tuiles
        for tile in self.map.tiles:
            if tile.id in {"Collision", "Bounce"} and not DEBUG_MODE:
                continue
            tile.draw(self.map_surf)

        # Dessiner le trou
        pygame.draw.circle(
            surface=self.map_surf,
            color=pygame.Color("black"),
            center=(self.map.hole.x, self.map.hole.y),
            radius=20
        )

        # Dessiner les bonus
        for bonus in self.map.bonuses:
            bonus.draw_bonus(self.map_surf)

    def draw_players(self):
        """Dessine les joueurs et met en évidence le joueur actif"""
        # Dessiner tous les joueurs
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

    def draw_aiming_line(self, center, zoom):
        """Dessine la ligne de visée pour le tir"""
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

    def render_map_to_screen(self, screen, center, zoom):
        """Applique le zoom et rend la carte sur l'écran"""
        resize_size = (int(self.map_size[0] * zoom), int(self.map_size[1] * zoom))
        if zoom == DEFAULT_ZOOM:
            map_surf_resized = self.map_surf
        else:
            map_surf_resized = pygame.transform.scale(self.map_surf, resize_size)

        zoom_offset_x = int(self.map.camera.offset_X * zoom)
        zoom_offset_y = int(self.map.camera.offset_Y * zoom)
        m_x = center[0] - zoom_offset_x
        m_y = center[1] - zoom_offset_y
        screen.blit(map_surf_resized, (m_x, m_y))

    def draw(self, screen):
        """Dessine le niveau complet sur l'écran."""
        self.draw_map(screen)
        self.score_manager.draw(self.overlay_surf)
        self.broadcast_manager.draw(self.overlay_surf)
        screen.blit(self.overlay_surf, (0, 0))
        # print(self.map.camera.is_world_position_on_screen(self.cur_player.position.x, self.cur_player.position.y))

    def centerOnPlayer(self, player: Player):
        """Centre la caméra sur un joueur"""
        x = player.position.x
        y = player.position.y

        camera = self.map.camera
        camera.animator.posToPosAndZoom(camera, (x, y), DEFAULT_ZOOM, 100)

    def centerOnPlayers(self, players: list[Player]):
        """Centre la caméra sur tous les joueurs en ajustant le zoom"""
        camera = self.map.camera
        x, y = 0, 0
        for player in players:
            x += player.position.x
            y += player.position.y

        p_count = len(players)
        x /= p_count
        y /= p_count

        camera.animator.posToPosAndZoom(camera, (x, y), MIN_ZOOM, 7)
