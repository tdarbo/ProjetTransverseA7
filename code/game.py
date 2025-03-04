from settings import *
from scene_v2 import *

class Game:
    def __init__(self):
        # Initialize Pygame
        pygame.init()
        pygame.display.set_caption(GAME_NAME)

        # Set up the game window
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.running = True
        self.clock = pygame.time.Clock()
        self.time_delta = DEFAULT_TIME_DELTA

        # UI manager with pygame_gui
        self.ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), theme_path="../data/ui-theme.json")
        self.ui_manager.set_visual_debug_mode(UI_DEBUG_MODE)

        # Initialize the scene manager
        self.scene_manager = SceneManager()

        # Create and add the scenes
        main_menu_scene = MainMenuScene(self)
        self.scene_manager.add("main_menu_scene", main_menu_scene)
        ##
        game_scene = GameScene(self)
        self.scene_manager.add("game_scene", game_scene)

        self.scene_manager.change("main_menu_scene")

    def run(self):
        # Main game loop
        while self.running:
            # Calculate time delta
            self.time_delta = self.clock.tick(FPS) / 1000

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.scene_manager.process_event(event)

            # Update and draw the current scene
            self.scene_manager.update(self.time_delta)
            self.scene_manager.draw(self.screen)

            # Update the display
            pygame.display.flip()

if __name__ == "__main__":
    # Create a game instance and run it
    game = Game()
    game.run()