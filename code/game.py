import os

from settings import *
from pygame.locals import *
from scene_config import ConfigurationScene
from scene_manager import SceneManager
from scene_play import PlayScene
from scene_start_menu import StartMenuScene
from sound import SoundManager
from pygame_gui.core import ObjectID
from interface_manager import InterfaceManager


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()  # Initialisation du système audio de pygame
        pygame.display.set_caption(GAME_NAME)  # Titre de la fenêtre
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, K_SPACE, K_h, K_e, MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP])
        # flags = FULLSCREEN | DOUBLEBUF

        # Chargez l'image du logo
        logo_path = '../asset/image/goat_logo.png'  # Chemin direct vers le logo
        logo = pygame.image.load(logo_path)

        icon_path = '../asset/image/goat_icon.ico'  # Chemin direct vers le logo
        icon = pygame.image.load(icon_path)

        # Définissez l'icône de la fenêtre (doit être fait AVANT set_mode)
        pygame.display.set_icon(logo)

        flags = DOUBLEBUF
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags, 24)

        self.running = True
        self.clock = pygame.time.Clock()
        self.dt = DELTA_TIME  # Temps entre les updates de pygame

        if not DEBUG_MODE:
            # Affichage du splash screen de lancement
            self.screen.blit(SPLASH_SCREEN, (0, 0))
            pygame.display.flip()

        self.maps = MAPS
        self.game_info = dict()  # Infos d'une partie

        # Audio : lance la musique de lancement
        self.sound_manager = SoundManager()
        self.sound_manager.play_music(MUSICS["launch"], loops=0)

        # Gestionnaire d'interface UI avec pygame_gui
        self.ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), theme_path="../data/ui-theme.json")
        self.ui_manager.set_visual_debug_mode(DEBUG_MODE)

        # Gestionnaire de scènes
        # On charge les trois scènes principales
        self.scene_manager = SceneManager()
        self.scene_manager.add("start_menu_scene", StartMenuScene(1, self))
        self.scene_manager.add("config_scene", ConfigurationScene(2, self))
        self.scene_manager.add("play_scene", PlayScene(3, self))

        # En mode debug on saute le menu et on va directement dans la scène de jeu
        if DEBUG_MODE:
            self.game_info = DEBUG_CONFIG
            self.scene_manager.change("play_scene")
        else:
            self.scene_manager.change("start_menu_scene")

        self.error_window = None  # Pour afficher des messages d'erreur

        # Petite pause avant avant d'afficher le menu principal
        # C'est utile pour afficher le splash screen
        pygame.time.wait(3000)

        # Création des interfaces "règles" et "crédits"
        self.interface_manager = InterfaceManager()
        self.build_rules_window()
        self.build_credits_window()

    def run(self):
        # Boucle principale du jeu
        clock = pygame.time.Clock()

        while self.running:
            # Mise à jour du delta time
            # Permet de gérer la physique de manière "constante"
            self.dt = self.clock.tick(FPS) / 1000

            # Gestion des événements pygame
            for event in pygame.event.get():
                # On gère les boutons de l'interface règles et crédits
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    ids = event.ui_element.get_object_ids()
                    if "#rules_menu_close_btn" in ids:
                        self.toggle_rules_window()
                    elif "#credits_menu_close_btn" in ids:
                        self.toggle_credits_window()
                if event.type == pygame.QUIT:
                    self.running = False

                # On propage les events aux scènes
                # et aussi à pygame_gui pour les interfaces
                self.scene_manager.process_event(event)
                self.ui_manager.process_events(event)

            # Mise à jour et affichage de la scène actuelle
            self.scene_manager.update(self.dt)
            self.scene_manager.draw(self.screen)

            # Mise à jour et affichage de l'interface utilisateur
            self.ui_manager.update(self.dt)
            self.ui_manager.draw_ui(self.screen)

            pygame.display.flip()

    def manage_error(self, error_message, title="Erreur"):
        """
        Crée et affiche une fenêtre d'erreur au centre de l'écran.
        Une seule fenêtre peut être affichée à la fois.
        """
        if self.error_window is not None:
            self.error_window.kill()
            self.error_window = None

        error_rect = pygame.rect.Rect(
            WINDOW_WIDTH // 2 - WINDOW_ERROR_WIDTH // 2,
            WINDOW_HEIGHT // 2 - WINDOW_ERROR_HEIGHT // 2,
            WINDOW_ERROR_WIDTH,
            WINDOW_ERROR_HEIGHT
        )

        self.error_window = pygame_gui.windows.UIMessageWindow(
            rect=error_rect,
            html_message=error_message,
            manager=self.ui_manager,
            window_title=title,
            always_on_top=True,
        )

    def build_rules_window(self):
        """
        Construction de la fenêtre des règles du jeu.
        Elle est invisible par défaut
        """
        container = pygame_gui.core.UIContainer(
            starting_height=10,
            relative_rect=(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            manager=self.ui_manager,
            visible=0,
        )
        pygame_gui.elements.UIImage(
            starting_height=11,
            relative_rect=(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            image_surface=RULES_IMAGE,
            manager=self.ui_manager,
            image_is_alpha_premultiplied=False,
            container=container,
            visible=0,
            scale_func=pygame.transform.scale
        )
        pygame_gui.elements.UIButton(
            anchors={"top": "bottom", "centerx": "centerx"},
            starting_height=12,
            relative_rect=pygame.Rect((OVERLAY_MENU_MARGIN, -INPUT_HEIGHT - OVERLAY_MENU_MARGIN),
                                      (INPUT_WIDTH, INPUT_HEIGHT)),
            text='Fermer',
            manager=self.ui_manager,
            container=container,
            object_id=ObjectID(class_id="button_secondary", object_id="#rules_menu_close_btn"),
            visible=0,
        )
        self.interface_manager.add("rules", container)

    def toggle_rules_window(self):
        self.interface_manager.toggle("rules")

    def build_credits_window(self):
        """
        Construction de la fenêtre des crédits du jeu.
        Ell est aussi invisible par défaut
        """
        container = pygame_gui.core.UIContainer(
            starting_height=13,
            relative_rect=(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            manager=self.ui_manager,
            visible=0,
        )
        pygame_gui.elements.UIImage(
            starting_height=14,
            relative_rect=(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            image_surface=CREDITS_IMAGE,
            manager=self.ui_manager,
            image_is_alpha_premultiplied=False,
            container=container,
            visible=0,
            scale_func=pygame.transform.scale
        )
        pygame_gui.elements.UIButton(
            anchors={"top": "bottom", "centerx": "centerx"},
            starting_height=15,
            relative_rect=pygame.Rect((OVERLAY_MENU_MARGIN, -INPUT_HEIGHT - OVERLAY_MENU_MARGIN),
                                      (INPUT_WIDTH, INPUT_HEIGHT)),
            text='Fermer',
            manager=self.ui_manager,
            container=container,
            object_id=ObjectID(class_id="button_secondary", object_id="#credits_menu_close_btn"),
            visible=0,
        )
        self.interface_manager.add("credits", container)

    def toggle_credits_window(self):
        """Affiche ou masque la fenêtre des crédits"""
        self.interface_manager.toggle("credits")
