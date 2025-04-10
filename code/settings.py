import pygame
import pygame_gui
from pygame.math import Vector2 as Vector

GAME_NAME = "GOAT"
GAME_VERSION = "1.0"

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60
DELTA_TIME = 0

# Physic
VELOCITY_THRESHOLD = 10
MAX_PLAYER_VELOCITY = Vector(1000, 1000)
FORCE_MULTIPLIER = 5
BALL_RADIUS = 15
TILE_SIZE = 64
BALL_MASS = 0.05
GROUND_GRASS_FRICTION = 0.06
GROUND_SAND_FRICTION = 0.30
GROUND_ICE_FRICTION = 0.02

INPUT_WIDTH = 300
INPUT_HEIGHT = 52
INPUTS_GAP = 20
PANEL_WIDTH = 500
PANEL_HEIGHT = WINDOW_HEIGHT + 10
PANEL_LAYOUT = pygame.Rect(
    (WINDOW_WIDTH - PANEL_WIDTH) // 2,
    -5,
    PANEL_WIDTH,
    PANEL_HEIGHT
)
PANEL_MARGINS = {
    "top": 100,
    "left": 50,
    "right": 50,
    "bottom": 50
}

DEFAULT_GAME_DICTIONARY = {"players": 1, "holes": 1, "names": []}
PLAYER_COLORS = [(255, 0, 0), (0, 0, 255), (0, 255, 0), (255, 255, 0), (0, 255, 255), (255, 0, 255)]

SCENE_BG_IMAGE = loadingScreen = pygame.transform.scale(
    pygame.image.load('../asset/image/terrain_bg.jpg'),
    (WINDOW_WIDTH, WINDOW_HEIGHT)
)

DEBUG_MODE = True
DEBUG_CONFIG = {'players':1,'holes':4,'names':["player0"]}

ASSET_PATH = "../asset"
UI_THEME_PATH = "../data/ui-theme.json"
FONT_PATH = "../asset/font/font-regular-v2.ttf"

MAX_ZOOM = 4
MIN_ZOOM = 0.5
