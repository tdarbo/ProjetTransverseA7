from settings import *
from scene import *

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption(GAME_NAME)

        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.running = True
        self.clock = pygame.time.Clock()
        self.time_delta = DEFAULT_TIME_DELTA
        # Interfaces avec pygame_ui
        self.ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), theme_path="../data/ui-theme.json")
        self.ui_manager.set_visual_debug_mode(UI_DEBUG_MODE)

        SPLASH_SCREEN_SCENE = SplashScreenScene()
        MAIN_MENU_SCENE = MainMenuScene(self.ui_manager)

        # Gestion des scenes du jeu
        self.scene_manager = SceneManager()
        self.scene_manager.add("splash", SPLASH_SCREEN_SCENE)
        self.scene_manager.add("main", MAIN_MENU_SCENE)
        self.scene_manager.change("main")

    def run(self):
        while self.running:
            self.time_delta = self.clock.tick(FPS) / 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                self.scene_manager.process_event(event)
                self.ui_manager.process_events(event)

            self.screen.fill(WHITE)

            self.scene_manager.update(self.time_delta)
            self.scene_manager.draw(self.screen)
            self.ui_manager.update(self.time_delta)
            pygame.display.flip()

if __name__ == "__main__":
    game = Game()
    game.run()