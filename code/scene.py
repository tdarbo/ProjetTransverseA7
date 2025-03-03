from settings import *


class SceneManager:
    """Allows adding and managing multiple scenes."""

    def __init__(self):
        """Initializes the scene manager."""
        self.scenes = {}
        self.current_scene = None

    def add(self, scene_name, scene):
        """
        Adds a scene to the manager.
        :param scene_name: The name of the scene.
        :type scene_name: str
        :param scene: The scene instance.
        :type scene: Scene
        """
        self.scenes[scene_name] = scene

    def change(self, scene_name):
        """
        Changes the active scene.
        :param scene_name: The name of the scene to change to.
        :type scene_name: str
        """
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]
            if DEBUG_MODE:
                print(f"[SceneManager] Changing scene {scene_name}")
        else:
            if DEBUG_MODE:
                print(f"[SceneManager] Unknown scene {scene_name}")

    # Basic Pygame methods ---
    def process_event(self, event):
        """
        Processes an event.
        :param event: The event to process.
        :type event: pygame.event.Event
        """
        self.current_scene.process_event(event)

    def update(self, dt):
        """
        Updates the current scene logic.
        :param dt: Time delta since the last update.
        :type dt: float
        """
        self.current_scene.update(dt)

    def draw(self, screen):
        """
        Draws the current scene on the screen.
        :param screen: The screen to draw on.
        :type screen: pygame.Surface
        """
        self.current_scene.draw(screen)


class Scene:
    def __init__(self):
        pass

    # Basic methods to create a scene ---
    def process_event(self, event):
        """
        Processes an event.
        :param event: The event to process.
        :type event: pygame.event.Event
        """
        pass

    def update(self, dt):
        """
        Updates the scene logic.
        :param dt: Time delta since the last update.
        :type dt: float
        """
        pass

    def draw(self, screen):
        """
        Draws the scene on the screen.
        :param screen: The screen to draw on.
        :type screen: pygame.Surface
        """
        pass


class MainMenuScene(Scene):
    def __init__(self, game):
        super().__init__()

        # Game instance
        self.game = game

        # UI manager with pygame_gui
        self.ui_manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT), theme_path="../data/ui-theme.json")
        self.ui_manager.set_visual_debug_mode(UI_DEBUG_MODE)

        # UI elements
        self.panel = pygame_gui.elements.UIPanel(
            relative_rect=DEFAULT_MENU_LAYOUT,
            manager=self.ui_manager,
            margins={
                'top': 100,
                'left': 50,
                'right': 50,
                'bottom': 50
            }
        )
        self.game_name_label = pygame_gui.elements.UILabel(
            text=GAME_NAME,
            manager=self.ui_manager,
            container=self.panel,
            relative_rect=pygame.Rect((0, 0, -1, 30)),
            anchors={
                'centerx': 'centerx',
            }
        )
        self.singleplayer_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 20), (300, 50)),
            text='Solo',
            manager=self.ui_manager,
            container=self.panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': self.game_name_label
            }
        )
        self.multiplayer_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 20), (300, 50)),
            text='Multiplayer',
            manager=self.ui_manager,
            container=self.panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': self.singleplayer_btn
            }
        )
        self.rules_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 20), (300, 50)),
            text='Rules',
            manager=self.ui_manager,
            container=self.panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': self.multiplayer_btn
            }
        )
        self.settings_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 20), (300, 50)),
            text='Settings',
            manager=self.ui_manager,
            container=self.panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': self.rules_btn
            }
        )
        self.exit_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 20), (300, 50)),
            text='Exit',
            manager=self.ui_manager,
            container=self.panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': self.settings_btn
            }
        )

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.singleplayer_btn:
                print("SinglePlayer")
            elif event.ui_element == self.multiplayer_btn:
                print("Multiplayer")
            elif event.ui_element == self.rules_btn:
                print("Rules")
            elif event.ui_element == self.settings_btn:
                print("Settings")
            elif event.ui_element == self.exit_btn:
                print("Exit")
                self.game.running = False

        self.ui_manager.process_events(event)

    def update(self, delta_time):
        self.ui_manager.update(delta_time)

    def draw(self, screen):
        screen.fill('red')
        self.ui_manager.draw_ui(screen)
