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
        pygame.mixer.init()
        pygame.display.set_caption(GAME_NAME)
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, K_SPACE, K_h, K_e, MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP])
        # flags = FULLSCREEN | DOUBLEBUF
        flags = DOUBLEBUF
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags, 24)
        self.running = True
        self.clock = pygame.time.Clock()
        self.dt = DELTA_TIME

        if not DEBUG_MODE:
            # Charger et afficher le splash screen
            self.screen.blit(SPLASH_SCREEN, (0, 0))
            pygame.display.flip()

        self.maps = MAPS

        self.game_info = dict()

        # Initialize sound
        self.sound_manager = SoundManager()
        self.sound_manager.play_music(MUSICS["launch"], loops=0)

        self.ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), theme_path="../data/ui-theme.json")
        self.ui_manager.set_visual_debug_mode(DEBUG_MODE)

        self.scene_manager = SceneManager()
        self.scene_manager.add("start_menu_scene", StartMenuScene(1, self))
        self.scene_manager.add("config_scene", ConfigurationScene(2, self))
        self.scene_manager.add("play_scene", PlayScene(3, self))

        self.interface_manager = InterfaceManager()

        if DEBUG_MODE:
            self.game_info = DEBUG_CONFIG
            self.scene_manager.change("play_scene")
        else:
            self.scene_manager.change("start_menu_scene")

        self.error_window = None

        # Attendre un court instant
        pygame.time.wait(3000)

        # Création des menus accessible dans tout le jeu
        self.build_rules_window()
        self.build_credits_window()

    def run(self):
        clock = pygame.time.Clock()

        # Main game loop
        while self.running:
            # Calculate time delta
            self.dt = self.clock.tick(FPS) / 1000

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    ids = event.ui_element.get_object_ids()
                    if "#rules_menu_close_btn" in ids:
                        self.toggle_rules_window()
                    elif "#credits_menu_close_btn" in ids:
                        self.toggle_credits_window()
                if event.type == pygame.QUIT:
                    self.running = False
                self.scene_manager.process_event(event)
                self.ui_manager.process_events(event)

            # Update and draw the current scene
            self.scene_manager.update(self.dt)
            self.scene_manager.draw(self.screen)

            # Update and draw the user interface
            self.ui_manager.update(self.dt)
            self.ui_manager.draw_ui(self.screen)
            # Update the display
            pygame.display.flip()

    def manage_error(self, error_message, title="Erreur"):
        """
        Affiche une fenêtre d'erreur avec le message fourni.
        Si une fenêtre d'erreur est déjà affichée, elle est remplacée par la nouvelle.

        :param error_message: Message d'erreur à afficher (peut contenir du HTML).
        :param title: Titre de la fenêtre d'erreur.
        """
        # Si une fenêtre d'erreur existe déjà, la détruire
        if self.error_window is not None:
            self.error_window.kill()
            self.error_window = None

        # Définir une zone pour la fenêtre d'erreur (ici, centrée sur l'écran)
        error_rect = pygame.rect.Rect(
            WINDOW_WIDTH // 2 - WINDOW_ERROR_WIDTH // 2,
            WINDOW_HEIGHT // 2 - WINDOW_ERROR_HEIGHT // 2,
            WINDOW_ERROR_WIDTH,
            WINDOW_ERROR_HEIGHT
        )

        # Créer la fenêtre d'erreur et la stocker
        self.error_window = pygame_gui.windows.UIMessageWindow(
            rect=error_rect,
            html_message=error_message,
            manager=self.ui_manager,
            window_title=title,
            always_on_top=True,
        )

    def build_rules_window(self):
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
        self.interface_manager.toggle("credits")

if __name__ == "__main__":
    # Create a game instance
    game = Game()
    game.run()
