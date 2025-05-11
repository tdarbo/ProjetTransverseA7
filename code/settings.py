import pygame
import pygame_gui
from pygame.math import Vector2 as Vector

## Chemins des fichiers du jeu
ASSET_PATH = "../asset"
UI_THEME_PATH = "../data/ui-theme.json"
FONT_PATH = "../asset/font/font-regular-v2.ttf"
MAPS = {
    "0": {
        "name": "hole1",
        "par": 4,
        "path": "../asset/TiledProject/maps/hole1.tmx",
        "difficulty": "easy"
    },
    "1": {
        "name": "Entre les lacs",
        "par": 4,
        "path": "../asset/TiledProject/maps/Entre_les_lacs.tmx",
        "difficulty": "easy"
    },
    "2": {
        "name": "Glissade mortelle",
        "par": 4,
        "path": "../asset/TiledProject/maps/Glissade_mortelle.tmx",
        "difficulty": "easy"
    },
    "3": {
        "name": "Coeur",
        "par": 5,
        "path": "../asset/TiledProject/maps/Coeur.tmx",
        "difficulty": "medium"
    },
    "4": {
        "name": "Détour obstrué",
        "par": 5,
        "path": "../asset/TiledProject/maps/Détour_obstrué.tmx",
        "difficulty": "medium"
    },
    "5": {
        "name": "Dédale désertique",
        "par": 6,
        "path": "../asset/TiledProject/maps/Dédale_desertique.tmx",
        "difficulty": "medium"
    },
    "6": {
        "name": "Descente aux enfers",
        "par": 7,
        "path": "../asset/TiledProject/maps/Descente_aux_enfers.tmx",
        "difficulty": "hard"
    },
    "7": {
        "name": "Île spirale",
        "par": 8,
        "path": "../asset/TiledProject/maps/Île_spirale.tmx",
        "difficulty": "hard"
    },
    "8": {
        "name": "Sablier du temps perdu",
        "par": 7,
        "path": "../asset/TiledProject/maps/Sablier_du_temps_perdu.tmx",
        "difficulty": "hard"
    },
    "9": {
        "name": "Deux lunes",
        "par": 7,
        "path": "../asset/TiledProject/maps/Deux_lunes.tmx",
        "difficulty": "hard"
    },
    "10": {
        "name": "Donut dopé",
        "par": 4,
        "path": "../asset/TiledProject/maps/Donut_dopé.tmx",
        "difficulty": "medium"
    },
    "11": {
        "name": "Long chemin",
        "par": 6,
        "path": "../asset/TiledProject/maps/Long_chemin.tmx",
        "difficulty": "easy"
    },
    "12": {
        "name": "Traversée des anneaux",
        "par": 4,
        "path": "../asset/TiledProject/maps/Traversée_des_anneaux.tmx",
        "difficulty": "medium"
    },
    "13": {
        "name": "Rétropédalage",
        "par": 3,
        "path": "../asset/TiledProject/maps/Rétropédalage.tmx",
        "difficulty": "easy"
    },
}

## Paramètres de configuration du jeu
GAME_NAME = "GOAT"
GAME_VERSION = "1.0"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
TILE_SIZE = 63
BALL_RADIUS = 15

## Paramètres de configuration d'une partie
MAX_PLAYERS_NUMBER = 5
MAX_HOLES_NUMBER = 5
MAX_PLAYER_NAME_LEN = 12
DEFAULT_GAME_DICTIONARY = {"players": 1, "holes": 1, "names": []}
PLAYER_COLORS = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255)]

## Variables physiques
DELTA_TIME = 0
VELOCITY_THRESHOLD = 10
MAX_PLAYER_VELOCITY = Vector(1000, 1000)
FORCE_MULTIPLIER = 5
BALL_MASS = 0.05
GROUND_GRASS_FRICTION = 0.06
GROUND_SAND_FRICTION = 0.30
GROUND_ICE_FRICTION = 0.02

## Paramètres des composants d'interfaces
INPUT_WIDTH = 300
INPUT_HEIGHT = 52
INPUTS_GAP = 10
PANEL_WIDTH = 500
PANEL_HEIGHT = WINDOW_HEIGHT + 10
PANEL_LAYOUT = pygame.Rect((WINDOW_WIDTH - PANEL_WIDTH) // 2, -5, PANEL_WIDTH, PANEL_HEIGHT)
PANEL_MARGINS = {
    "top": 100,
    "bottom": 50,
    "left": 50,
    "right": 50

}
SCENE_BG_IMAGE = pygame.transform.scale(
    pygame.image.load('../asset/image/terrain_bg.jpg'),
    (WINDOW_WIDTH, WINDOW_HEIGHT)
)
SPLASH_SCREEN = pygame.transform.scale(
    pygame.image.load('../asset/image/splash_bg.png'),
    (WINDOW_WIDTH, WINDOW_HEIGHT)
)
SPLASH_BG = pygame.transform.scale(
    pygame.image.load('../asset/image/empty_splash_bg.png'),
    (WINDOW_WIDTH, WINDOW_HEIGHT)
)

# DEBUG
DEBUG_MODE = False
DEBUG_CONFIG = {'players': 2, 'holes': 4, 'names': ["player0","player1"]}

## Paramètres de la caméra
DEFAULT_ZOOM = 1
MAX_ZOOM = 2
MIN_ZOOM = 0.5

## Dimensions de la fenêtre d'erreur
WINDOW_ERROR_WIDTH = PANEL_WIDTH - 100
WINDOW_ERROR_HEIGHT = PANEL_HEIGHT // 2

## Dimensions du menu du score
OVERLAY_CELL_WIDTH = 100  # Largeur d'une cellule
OVERLAY_CELL_HEIGHT = 10  # Hauteur d'une cellule
OVERLAY_CELL_GAP = 15  # Espace entre cellules
OVERLAY_MENU_PADDING = 20  # Espace entre le contenu et le menu
OVERLAY_MENU_MARGIN = 20  # Espace entre le menu et les bords de l'écran
OVERLAY_MENU_FONT_SIZE = 11  # Taille de la police du menu

## Musiques et sons
MUSICS = {
    "launch": "../asset/musics/Lancement jeu.wav",
    "game1": "../asset/musics/Musique_Jeu.wav",
    "game2": "../asset/musics/Musique_jeu-v2.wav",
}

SOUNDS = {
    "ball": "../asset/musics/Balle.wav",
    "clic": "../asset/musics/Clic.wav",
    "bounce": "../asset/musics/Rebond.wav",
    "victory": "../asset/musics/Victoire !.wav",
    "boost": "../asset/musics/boost.wav",
    "magnet": "../asset/musics/aimant.wav",
    "water": "../asset/musics/eau.wav"
}
VOLUME_SOUND = 0.5
VOLUME_MUSIC = 0.5
