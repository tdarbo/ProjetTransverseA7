import random
from settings import *
from player import Player
from level import Level
from score import ScoreManager
from map import Map
from scene_manager import Scene
from broadcast import BroadcastManager
from ui_text import Text

class PlayScene(Scene):
    """Gestion de la scène principale du jeu."""

    # États possibles de la partie
    STATE_LEVEL_INFO = "level_info"  # écran d'info du niveau
    STATE_PLAYING = "playing"  # jeu en cours
    STATE_END_INFO = "end_info"  # écran de fin de partie
    DURATION_END_INFO = 5
    DURATION_LEVEL_INFO = 3

    def __init__(self, height_index, game):
        super().__init__(height_index, game)
        self.game = game
        self.players: list[Player] = []
        self.selected_maps = []
        self.cur_level: Level = None
        self.cur_level_index: int = 0

        self.score_manager: ScoreManager = None
        self.broadcast_manager: BroadcastManager = BroadcastManager()

        # Attributs pour la gestion des états
        self.current_state: str = self.STATE_LEVEL_INFO
        self.state_timer: float = 0  # Compteur en millisecondes
        self.state_duration: int = 3000  # Durée en millisecondes (3 secondes)

        # Surfaces pour les écrans d'information
        self.level_info_surface: pygame.Surface = pygame.Surface(self.game.screen.get_size())
        self.end_info_surface: pygame.Surface = pygame.Surface(self.game.screen.get_size())

        # Nouvel attribut pour indiquer si la partie est terminée
        self.finished: bool = False

    def on_enter(self):
        game_info = self.game.game_info
        self.players = self.create_players(game_info.get("names", []))
        holes_number = game_info.get("holes", 1)

        self.score_manager = ScoreManager(self.players, holes_number)
        self.select_maps(holes_number)
        self.cur_level_index = -1
        self.finished = False

        self.load_level()
        self.game.sound_manager.play_music(MUSICS["game1"])

    def select_maps(self, count):
        """Sélectionne 'count' maps uniques aléatoirement."""
        maps = list(self.game.maps.values())
        self.selected_maps = random.sample(maps, count)

    def create_players(self, names):
        """Instancie les joueurs avec leur couleur et nom."""
        players = []
        for i in range(len(names)):
            color = PLAYER_COLORS[i % len(PLAYER_COLORS)]
            players.append(
                Player(
                    color=color,
                    position=Vector(0, 0),
                    radius=BALL_RADIUS,
                    mass=BALL_MASS,
                    name=names[i]
                )
            )
        return players

    def create_level(self, hole_index, map_info):
        """Crée un niveau à partir d'une map."""
        return Level(
            hole_index=hole_index,
            map_obj=Map(map_info, self.game.screen),
            players=self.players,
            score_manager=self.score_manager,
            broadcast_manager=self.broadcast_manager,
            game=self.game,
        )

    def load_level(self):
        """Charge le niveau suivant ou termine la partie."""
        self.cur_level_index += 1

        if self.cur_level_index < len(self.selected_maps):
            self.reset_players()
            map_info = self.selected_maps[self.cur_level_index]

            self.cur_level = self.create_level(self.cur_level_index, map_info)
            self.score_manager.set_current_hole(self.cur_level_index)

            # Configurer l'état pour afficher les infos du niveau
            self.build_level_info_surface()
            self.current_state = self.STATE_LEVEL_INFO
            self.state_timer = pygame.time.get_ticks()
        else:
            # Marquer la partie comme terminée
            self.finished = True
            self.cur_level = None
            self.build_end_info_surface()
            self.current_state = self.STATE_END_INFO
            self.state_timer = pygame.time.get_ticks()

    def next_level(self):
        """Passe au niveau suivant ou termine la partie."""
        if not self.finished:
            self.load_level()

    def reset_players(self):
        for player in self.players:
            player.hide = False
            player.reset()

    def process_event(self, event):
        if (self.current_state == self.STATE_PLAYING) and not self.finished:
            self.cur_level.process_event(event)

    def update(self, dt):
        current_time = pygame.time.get_ticks()

        # Gérer les transitions d'état
        if self.current_state == self.STATE_LEVEL_INFO:
            if current_time - self.state_timer >= self.state_duration:
                self.current_state = self.STATE_PLAYING
        elif self.current_state == self.STATE_PLAYING:
            if self.cur_level:
                self.cur_level.update(dt)
                if self.cur_level.finished:
                    self.next_level()
        elif self.current_state == self.STATE_END_INFO:
            if current_time - self.state_timer >= self.state_duration:
                self.leave_game()

    def draw(self, screen):
        screen.fill("#BDDFFF")
        if self.current_state == self.STATE_LEVEL_INFO:
            # On affiche l'écran d'info du niveau
            screen.blit(self.level_info_surface, (0, 0))
        elif self.current_state == self.STATE_PLAYING:
            # On affiche le jeu
            if self.cur_level:
                self.cur_level.draw(screen)
        elif self.current_state == self.STATE_END_INFO:
            # On affiche l'écran de fin
            screen.blit(self.end_info_surface, (0, 0))

    def leave_game(self):
        print("Partie terminée ! Scores finaux :")
        self.game.scene_manager.change("start_menu_scene")

    def build_level_info_surface(self):
        """Construit la surface pour l'écran d'information de niveau."""
        self.level_info_surface.blit(SPLASH_BG, (0, 0))

        Text(
            text=f"Trou n°{self.cur_level_index + 1}",
            pos=(
                self.game.screen.get_width() // 2,
                self.game.screen.get_height() // 2 - 65
            ),
            font_size=17,
            color="black",
            align="center"
        ).draw(self.level_info_surface)

        Text(
            text=self.cur_level.map.infos["name"],
            pos=(
                self.game.screen.get_width() // 2,
                self.game.screen.get_height() // 2
            ),
            font_size=40,
            color="#D55534",
            align="center"
        ).draw(self.level_info_surface)

        Text(
            text=f"Par {self.cur_level.map.infos["par"]}",
            pos=(
                self.game.screen.get_width() // 2,
                self.game.screen.get_height() // 2 + 65
            ),
            font_size=16,
            color="black",
            align="center"
        ).draw(self.level_info_surface)

    def build_end_info_surface(self):
        """Construit la surface pour l'écran de fin de partie."""
        self.end_info_surface.blit(SPLASH_BG, (0, 0))

        Text(
            text="Partie terminée !",
            pos=(
                self.game.screen.get_width() // 2,
                self.game.screen.get_height() // 2 - 125
            ),
            font_size=40,
            color="#D55534",
            align="center"
        ).draw(self.end_info_surface)

        Text(
            text="Tableau récapitulatif des scores :",
            pos=(
                self.game.screen.get_width() // 2,
                self.game.screen.get_height() // 2 - 60
            ),
            font_size=14,
            color="black",
            align="center"
        ).draw(self.end_info_surface)

        self.score_manager.draw_menu(
            start_x=self.game.screen.get_width() // 2 - (self.score_manager.menu_width // 2) + 50,
            start_y=self.game.screen.get_height() // 2 - self.score_manager.menu_height // 2 + 60,
            text_color="black",
            screen=self.end_info_surface
        )
