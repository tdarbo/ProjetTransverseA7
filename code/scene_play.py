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
    STATE_LEVEL_INFO = "level_info"
    STATE_PLAYING = "playing"
    STATE_END_INFO = "end_info"
    DURATION_END_INFO = 7000
    DURATION_LEVEL_INFO = 3000

    def __init__(self, height_index, game):
        super().__init__(height_index, game)
        self.game = game

        # Liste des joueurs actifs
        self.players: list[Player] = []

        # Liste des cartes sélectionnées
        self.selected_maps = []

        # Niveau actuel
        self.cur_level: Level = None
        self.cur_level_index: int = 0  # Index du niveau en cours

        self.score_manager: ScoreManager = None
        self.broadcast_manager: BroadcastManager = BroadcastManager()

        # État de la scène ("level_info", "playing", "end_info")
        self.current_state: str = self.STATE_LEVEL_INFO
        self.state_timer: float = 0  # Temps du début de l'état
        # Surface pour afficher les états
        self.level_info_surface: pygame.Surface = pygame.Surface(self.game.screen.get_size())
        self.end_info_surface: pygame.Surface = pygame.Surface(self.game.screen.get_size())

        # Indicateur de fin de partie
        self.finished: bool = False

    def on_enter(self):
        """Initialise la partie à l'entrée dans la scène."""
        game_info = self.game.game_info

        # Création des joueurs
        self.players = self.create_players(game_info.get("names", []))

        # On récupère le nombre de trous
        holes_number = game_info.get("holes", 1)

        # On initialise les scores
        self.score_manager = ScoreManager(self.players, holes_number)

        # Sélection des maps
        self.select_maps(holes_number)

        # On réinitialise les variables du level
        self.cur_level_index = -1
        self.finished = False

        # Charge le premier niveau
        self.load_level()
        self.game.sound_manager.play_music(MUSICS["game1"])

    def select_maps(self, count):
        """Sélectionne les maps aléatoirement."""
        maps = list(self.game.maps.values())
        if DEBUG_MODE:
            self.selected_maps = maps  # En DEBUG_MODE, on garde toutes les maps
        else:
            self.selected_maps = random.sample(maps, count)  # Sélection aléatoire (et aussi sans doublon)

    def create_players(self, names):
        """Instancie les joueurs avec leur couleur et nom."""
        players = []
        for i in range(len(names)):
            color = PLAYER_COLORS[i % len(PLAYER_COLORS)]  # On attribue une couleur unique par joueur
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
            map_obj=Map(map_info, self.game.screen, self.broadcast_manager),
            players=self.players,
            score_manager=self.score_manager,
            broadcast_manager=self.broadcast_manager,
            game=self.game,
        )

    def load_level(self):
        """Charge le niveau suivant ou termine la partie si tous les niveaux sont terminés."""
        self.cur_level_index += 1

        if self.cur_level_index < len(self.selected_maps):
            # Il reste des niveaux à jouer
            self.reset_players()
            map_info = self.selected_maps[self.cur_level_index]

            # Création du niveau
            self.cur_level = self.create_level(self.cur_level_index, map_info)
            self.score_manager.set_current_hole(self.cur_level_index)

            # Passage à l'affichage d'info du niveau
            self.build_level_info_surface()
            self.current_state = self.STATE_LEVEL_INFO
            self.state_timer = pygame.time.get_ticks()
        else:
            # Tous les niveaux ont été joués
            self.finished = True
            self.cur_level = None

            # On affiche l’écran de fin
            self.build_end_info_surface()
            self.current_state = self.STATE_END_INFO
            self.state_timer = pygame.time.get_ticks()

    def next_level(self):
        """Passe au niveau suivant (ou affiche l’écran de fin)."""
        if not self.finished:
            self.load_level()

    def reset_players(self):
        """Réinitialise tous les joueurs pour le prochain niveau."""
        for player in self.players:
            player.hide = False
            player.reset()

    def process_event(self, event):
        if self.current_state == self.STATE_PLAYING and not self.finished:
            self.cur_level.process_event(event)

    def update(self, dt):
        """Met à jour l’état du jeu en fonction du temps et de l’état courant."""
        current_time = pygame.time.get_ticks()

        if self.current_state == self.STATE_LEVEL_INFO:
            if current_time - self.state_timer >= self.DURATION_LEVEL_INFO:
                self.current_state = self.STATE_PLAYING  # Lancer le jeu après l'affichage

        elif self.current_state == self.STATE_PLAYING:
            if self.cur_level:
                self.cur_level.update(dt)
                if self.cur_level.finished:
                    self.next_level()  # Niveau terminé, on passe au suivant

        elif self.current_state == self.STATE_END_INFO:
            if current_time - self.state_timer >= self.DURATION_END_INFO:
                self.leave_game()  # Fin de partie, retour au menu principal

    def draw(self, screen):
        """Affiche l’état courant du jeu sur l’écran."""
        screen.fill("#BDDFFF")  # Couleur de fond

        if self.current_state == self.STATE_LEVEL_INFO:
            screen.blit(self.level_info_surface, (0, 0))  # Affiche infos du niveau
        elif self.current_state == self.STATE_PLAYING:
            if self.cur_level:
                self.cur_level.draw(screen)  # Affiche le niveau courant
        elif self.current_state == self.STATE_END_INFO:
            screen.blit(self.end_info_surface, (0, 0))  # On affiche l’écran de fin

    def leave_game(self):
        """Quitte la partie et revient au menu principal."""
        self.game.scene_manager.change("start_menu_scene")

    def build_level_info_surface(self):
        """Construit l’écran avec les infos de la carte."""
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
            text=f"Par {self.cur_level.map.infos['par']}",
            pos=(
                self.game.screen.get_width() // 2,
                self.game.screen.get_height() // 2 + 65
            ),
            font_size=16,
            color="black",
            align="center"
        ).draw(self.level_info_surface)

    def build_end_info_surface(self):
        """Construit l’écran final de fin de partie avec le récap des scores."""
        self.end_info_surface.blit(SPLASH_BG, (0, 0))

        Text(
            text="Partie terminée !",
            pos=(
                self.game.screen.get_width() // 2,
                self.game.screen.get_height() // 2 - 115
            ),
            font_size=40,
            color="#D55534",
            align="center"
        ).draw(self.end_info_surface)

        Text(
            text="Tableau récapitulatif des scores",
            pos=(
                self.game.screen.get_width() // 2,
                self.game.screen.get_height() // 2 - 70
            ),
            font_size=16,
            color="black",
            align="center"
        ).draw(self.end_info_surface)

        self.score_manager.draw_menu(
            start_x=self.game.screen.get_width() // 2 - self.score_manager.menu_width // 2 + 20,
            start_y=self.game.screen.get_height() // 2 - self.score_manager.menu_height // 2 + 70,
            text_color="black",
            screen=self.end_info_surface
        )
