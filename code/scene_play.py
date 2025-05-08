import random
from settings import *
from player import Player
from level import Level
from score import ScoreManager
from map import Map
from scene_manager import Scene
from broadcast import BroadcastManager


class PlayScene(Scene):
    """Gestion de la scène principale du jeu"""

    def __init__(self, height_index, game):
        super().__init__(height_index, game)
        self.maps = game.maps
        self.screen = game.screen

        self.game_info = None

        # Création des joueurs et init score
        self.players = []
        self.score_manager = None
        self.broadcast_manager = None

        # Gestion des niveaux joués
        self.hole_number = 0
        self.levels_played = 0
        self.current_level = None


    def on_enter(self):
        self.game_info = self.game.game_info
        self.players = self.create_players()
        if self.game_info["holes"] :
            self.hole_number = self.game_info["holes"]
        else :
            self.hole_number = 1
        self.score_manager = ScoreManager(self.players, self.hole_number)
        self.broadcast_manager = BroadcastManager()
        self.levels_played = 0
        self.hole_number = self.hole_number
        self.current_level = None
        # Chargement du premier niveau
        self.load_next_level()
        self.game.sound_manager.play_music(MUSICS["game1"])

    def create_players(self):
        """Instancie les joueurs en utilisant les noms fournis."""
        players = []
        for i, name in enumerate(self.game_info.get("names", [])):
            player = Player(
                color=PLAYER_COLORS[i % len(PLAYER_COLORS)],
                position=Vector(0, 0),
                radius=BALL_RADIUS,
                mass=BALL_MASS,
                name=name
            )
            players.append(player)

        return players

    def create_level(self, hole_number, map_infos):
        """Crée un niveau à partir du path de la map."""
        tiled_map = Map(map_infos, self.screen)
        width, height = self.screen.get_size()
        level = Level(
            hole_number,
            tiled_map,
            self.players,
            self.score_manager,
            self.broadcast_manager,
            self.game,
        )
        return level

    def load_next_level(self):
        """Charge un niveau s'il en reste, sinon termine la partie."""
        if self.levels_played < self.hole_number:
            self.reset_players()
            map_key = random.choice(list(self.maps.keys()))
            map_infos = self.maps[map_key]
            self.current_level = self.create_level(self.levels_played, map_infos)
            self.levels_played += 1
            self.score_manager.set_current_hole(self.levels_played - 1)
            print("Current hole : ", self.levels_played - 1)
            print(f"Niveau {self.levels_played} chargé avec la map '{map_key}'.")
        else:
            self.current_level = None

    def next_level(self):
        """Passe au niveau suivant ou quitte le jeu."""
        if self.levels_played < self.hole_number:
            self.load_next_level()
        else:
            self.quit_game()

    def reset_players(self):
        for player in self.players:
            player.hide = False
            player.reset()

    def process_event(self, event):
        if self.current_level:
            self.current_level.process_event(event)

    def update(self, dt):
        if self.current_level:
            self.current_level.update(dt)
            if self.current_level.finished:
                self.next_level()

    def draw(self, screen):
        screen.fill("#BDDFFF")
        if self.current_level:
            self.current_level.draw(screen)

    def quit_game(self):
        """Affiche les scores finaux et ferme le jeu."""
        print("Partie terminée ! Scores finaux :")

