import pygame.rect
from pygame.locals import *
from settings import *
from scene_config import ConfigurationScene
from scene_manager import SceneManager
from scene_play import PlayScene
from scene_start_menu import StartMenuScene
from sound import SoundManager


class Game:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        pygame.display.set_caption(GAME_NAME)
        pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP, K_SPACE, K_h, K_e, MOUSEBUTTONDOWN, MOUSEMOTION, MOUSEBUTTONUP])
        # flags = FULLSCREEN | DOUBLEBUF
        flags = DOUBLEBUF
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags, 8)
        self.running = True
        self.clock = pygame.time.Clock()
        self.dt = DELTA_TIME

        if not DEBUG_MODE:
            # Charger et afficher le splash screen
            self.screen.blit(SPLASH_BG, (0, 0))
            pygame.display.flip()

        if DEBUG_MODE:
            self.maps = {
                "map1": "../asset/TiledProject/maps/hole1.tmx"
            }
        else:
            self.maps = {
                "map1": "../asset/TiledProject/maps/hole1.tmx",
                "map2": "../asset/TiledProject/maps/Entre_les_lacs.tmx",
                "map3": "../asset/TiledProject/maps/Glissade_mortelle.tmx",
                "map4": "../asset/TiledProject/maps/Coeur.tmx",
                "map5": "../asset/TiledProject/maps/Détour_obstrué.tmx",
                "map6": "../asset/TiledProject/maps/Dédale_desertique.tmx",
                "map7": "../asset/TiledProject/maps/Descente_aux_enfers.tmx",
                "map8": "../asset/TiledProject/maps/Île_spirale.tmx",
                "map9": "../asset/TiledProject/maps/Sablier_du_temps_perdu.tmx",
                "map10": "../asset/TiledProject/maps/Deux_lunes.tmx",
            }

        self.game_info = dict()
        

        self.ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), theme_path="../data/ui-theme.json")
        self.ui_manager.set_visual_debug_mode(DEBUG_MODE)

        self.scene_manager = SceneManager()
        self.scene_manager.add("start_menu_scene", StartMenuScene(1, self))
        self.scene_manager.add("config_scene", ConfigurationScene(2, self))
        self.scene_manager.add("play_scene", PlayScene(3, self))

        if DEBUG_MODE:
            self.game_info = DEBUG_CONFIG
            self.scene_manager.change("play_scene")
        else:
            self.scene_manager.change("start_menu_scene")

        self.error_window = None

        # Attendre un court instant
        pygame.time.wait(2000)

    def run(self):
        clock = pygame.time.Clock()

        # Main game loop
        while self.running:
            # Calculate time delta
            self.dt = self.clock.tick(FPS) / 1000

            # Event handling
            for event in pygame.event.get():
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
            self.sound_manager.play()
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
            WINDOW_WIDTH // 2 - WINDOW_ERROR_WIDTH//2,
            WINDOW_HEIGHT // 2 - WINDOW_ERROR_HEIGHT//2,
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


if __name__ == "__main__":
    # Create a game instance
    game = Game()
    game.run()
