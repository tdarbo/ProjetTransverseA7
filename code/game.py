from components_scene import ComponentsScene
from scene_config import ConfigurationScene
from scene_manager import *
from scene_play import PlayScene
from scene_start_menu import StartMenuScene


class Game:
    def __init__(self):
        """
        Initialize the game.
        """
        # Initialize Pygame
        pygame.init()
        pygame.display.set_caption(GAME_NAME)

        # Set up the game window
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.running = True
        self.clock = pygame.time.Clock()
        self.time_delta = DELTA_TIME

        # UI manager with pygame_gui
        self.ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), theme_path="../data/ui-theme.json")
        self.ui_manager.set_visual_debug_mode(DEBUG_MODE)

        # Initialize the scene manager
        self.scene_manager = SceneManager()
        # Create and add the scenes
        self.scene_manager.add("start_menu_scene", StartMenuScene(1, self))
        self.scene_manager.add("config_scene", ConfigurationScene(2, self))
        self.scene_manager.add("play_scene", PlayScene(3, self))
        self.scene_manager.add("components_scene", ComponentsScene(4, self))
        # Display default scene
        self.scene_manager.change("start_menu_scene")

        self.error_window = None

    def run(self):
        """
        Main game loop.
        """
        # Main game loop
        while self.running:
            # Calculate time delta
            self.time_delta = self.clock.tick(FPS) / 1000

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.scene_manager.process_event(event)
                self.ui_manager.process_events(event)

            # Update and draw the current scene
            self.scene_manager.update(self.time_delta)
            self.scene_manager.draw(self.screen)

            # Update and draw the user interface
            self.ui_manager.update(self.time_delta)
            self.ui_manager.draw_ui(self.screen)

            # Update the display
            pygame.display.flip()

    def manage_error(self, error_message, title="Error"):
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
        error_rect = pygame.Rect(WINDOW_WIDTH // 2 - 150, WINDOW_HEIGHT // 2 - 100, 300, 200)

        # Créer la fenêtre d'erreur et la stocker
        self.error_window = pygame_gui.windows.UIMessageWindow(
            rect=error_rect,
            html_message=error_message,
            manager=self.ui_manager,
            window_title=title,
            always_on_top=True
        )


if __name__ == "__main__":
    # Create a game instance and run it
    game = Game()
    game.run()
