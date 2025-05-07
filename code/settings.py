import pygame
import pygame_gui
from pygame.math import Vector2 as Vector

## Chemins des fichiers du jeu
ASSET_PATH = "../asset"
UI_THEME_PATH = "../data/ui-theme.json"
FONT_PATH = "../asset/font/font-regular-v2.ttf"

## Paramètres de configuration du jeu
GAME_NAME = "GOAT"
GAME_VERSION = "1.0"
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
TILE_SIZE = 64
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
SPLASH_BG = pygame.transform.scale(
    pygame.image.load('../asset/image/splash_bg.png'),
    (WINDOW_WIDTH, WINDOW_HEIGHT)
)

# DEBUG
DEBUG_MODE = False
DEBUG_CONFIG = {'players':2,'holes':4,'names':["player0"]}

## Paramètres de la caméra
MAX_ZOOM = 4
MIN_ZOOM = 0.5

## Dimensions de la fenêtre d'erreur
WINDOW_ERROR_WIDTH = PANEL_WIDTH - 100
WINDOW_ERROR_HEIGHT = PANEL_HEIGHT // 2

## Dimensions du menu du score
SCORE_CELL_WIDTH = 100 # Largeur d'une cellule
SCORE_CELL_HEIGHT = 10 # Hauteur d'une cellule
SCORE_CELL_GAP = 15 # Espace entre cellules
SCORE_MENU_PADDING = 20 # Espace entre le contenu et le menu
SCORE_MENU_MARGIN = 25 # Espace entre le menu et les bords de l'écran
SCORE_MENU_FONT_SIZE = 11 # Taille de la police du menu

## Musiques et sons
MUSICS = {"Lancement_jeu":"../asset/musics/Lancement jeu.wav",
          "jeu1":"../asset/musics/Lancement jeu.wav",
          "jeu2":"../asset/musics/Musique_jeu-v2.wav",
          }

SOUNDS = {"ball":"../asset/musics/Balle.wav",
          "clic":"../asset/musics/Clic.wav",
          "bounce":"../asset/musics/Rebond.wav",
          "victory":"../asset/musics/Victoire !.wav",
          }