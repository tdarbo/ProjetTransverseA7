from settings import *
import pygame
import pygame_gui


class SceneManager:
    def __init__(self):
        """
        Responsible for switching scenes
        """
        self.scenes = {}
        self.current_scene = None

    def add(self, scene_name, scene):
        """
        Add a new scene to the manager.

        :param scene_name: The name of the scene.
        :param scene: The scene object to add.
        """
        self.scenes[scene_name] = scene

    def change(self, scene_name):
        """
        Change the current scene to a new one. Before switching,
        the UI manager is reset to clear all UI elements.

        :param scene_name: The name of the scene to change to.
        """
        # If a scene is currently active, perform its cleanup
        if self.current_scene is not None:
            self.current_scene.on_exit()
            if DEBUG_MODE:
                print("[SceneManager] Exiting the current scene.")
        # Switch to the new scene and initialize it
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]
            self.current_scene.on_enter()
            if DEBUG_MODE:
                print(f"[SceneManager] Entering the new scene: '{scene_name}'.")
        else:
            if DEBUG_MODE:
                print(f"[SceneManager] Scene '{scene_name}' not found.")

    def process_event(self, event):
        """
        Process an event in the current scene.

        :param event: The event to process.
        """
        if self.current_scene:
            self.current_scene.process_event(event)

    def update(self, dt):
        """
        Update the current scene.

        :param dt: The time delta since the last update.
        """
        if self.current_scene:
            self.current_scene.update(dt)

    def draw(self, screen):
        """
        Draw the current scene.

        :param screen: The screen to draw on.
        """
        if self.current_scene:
            self.current_scene.draw(screen)


class Scene:
    def __init__(self):
        """
        Scene: Base class for scenes
        """
        self.ui_manager = None

    def on_enter(self):
        """
        Called when the scene is entered.
        """
        pass

    def on_exit(self):
        """
        Called when the scene is exited.
        Resets the UI manager to clear all UI elements.
        """
        if self.ui_manager:
            # Reset the UI manager to remove all created UI elements
            self.ui_manager.clear_and_reset()
            if DEBUG_MODE:
                print(f"[{self.__class__.__name__}] UI manager cleared and reset.")
        else:
            if DEBUG_MODE:
                print(f"[{self.__class__.__name__}] No UI manager to clear.")

    def process_event(self, event):
        """
        Process an event in the scene.

        :param event: The event to process.
        """
        pass

    def update(self, dt):
        """
        Update the scene.

        :param dt: The time delta since the last update.
        """
        pass

    def draw(self, screen):
        """
        Draw the scene.

        :param screen: The screen to draw on.
        """
        pass


class MainMenuScene(Scene):
    def __init__(self, game):
        """
        Initialize the main menu scene.

        :param game: The game object.
        """
        super().__init__()
        self.game = game
        # Use the shared UI manager from the Game object
        self.ui_manager = self.game.ui_manager
        self.scene_manager = self.game.scene_manager

    def on_enter(self):
        """
        Called when entering the main menu scene.
        Builds the main menu UI.
        """
        self.build_main_menu()
        if DEBUG_MODE:
            print("[MainMenuScene] Main menu UI created.")

    def build_main_menu(self):
        """
        Build the main menu UI elements.
        """
        panel = pygame_gui.elements.UIPanel(
            relative_rect=DEFAULT_MENU_LAYOUT,
            manager=self.ui_manager,
            margins={'top': 100, 'left': 50, 'right': 50, 'bottom': 50},
            object_id="main_menu_panel",
        )
        game_name_label = pygame_gui.elements.UILabel(
            text=GAME_NAME,
            manager=self.ui_manager,
            container=panel,
            relative_rect=pygame.Rect((0, 0, -1, 30)),
            anchors={'centerx': 'centerx'},
            object_id="main_menu_game_name",
        )
        play_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 20), (300, 50)),
            text='Play',
            manager=self.ui_manager,
            container=panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': game_name_label
            },
            object_id="main_menu_play_btn",
        )
        rules_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 20), (300, 50)),
            text='Rules',
            manager=self.ui_manager,
            container=panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': play_btn
            },
            object_id="main_menu_rules_btn",
        )
        settings_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 20), (300, 50)),
            text='Settings',
            manager=self.ui_manager,
            container=panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': rules_btn
            },
            object_id="main_menu_settings_btn",
        )
        exit_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 20), (300, 50)),
            text='Exit',
            manager=self.ui_manager,
            container=panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': settings_btn
            },
            object_id="main_menu_exit_btn",
        )

    def process_event(self, event):
        """
        Handle events in the main menu scene.

        :param event: The event to process.
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element.text == "Play":
                if DEBUG_MODE:
                    print("Play button pressed.")
                self.scene_manager.change("game_scene")
            elif event.ui_element.text == "Rules":
                if DEBUG_MODE:
                    print("Rules button pressed.")
            elif event.ui_element.text == "Settings":
                if DEBUG_MODE:
                    print("Settings button pressed.")
            elif event.ui_element.text == "Exit":
                if DEBUG_MODE:
                    print("Exit button pressed.")
                self.game.running = False

        self.ui_manager.process_events(event)

    def update(self, delta_time):
        """
        Update the main menu scene.

        :param delta_time: The time delta since the last update.
        """
        self.ui_manager.update(delta_time)

    def draw(self, screen):
        """
        Draw the main menu scene.

        :param screen: The screen to draw on.
        """
        screen.fill('black')
        self.ui_manager.draw_ui(screen)


class GameScene(Scene):
    def __init__(self, game):
        """
        Initialize the game scene.

        :param game: The game object.
        """
        super().__init__()
        self.game = game
        # Use the shared UI manager from the Game object
        self.ui_manager = self.game.ui_manager
        self.scene_manager = self.game.scene_manager

    def on_enter(self):
        """
        Called when entering the game scene. Builds the game UI.
        """
        self.build_hello()
        if DEBUG_MODE:
            print("[GameScene] Game UI created.")

    def build_hello(self):
        """
        Build the game UI elements.
        """
        game_name_label = pygame_gui.elements.UILabel(
            text=GAME_NAME + " Game",
            manager=self.ui_manager,
            relative_rect=pygame.Rect((0, 0, -1, 30)),
            anchors={'centerx': 'centerx'},
            object_id="game_scene_game_name",
        )
        back_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 20), (300, 50)),
            text='Back',
            manager=self.ui_manager,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': game_name_label
            },
            object_id="game_scene_back_btn",
        )

    def process_event(self, event):
        """
        Handle events in the game scene.

        :param event: The event to process.
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element.text == "Back":
                if DEBUG_MODE:
                    print("Back button pressed.")
                self.scene_manager.change("main_menu_scene")
        self.ui_manager.process_events(event)

    def update(self, delta_time):
        """
        Update the game scene.

        :param delta_time: The time delta since the last update.
        """
        self.ui_manager.update(delta_time)

    def draw(self, screen):
        """
        Draw the game scene.

        :param screen: The screen to draw on.
        """
        screen.fill('black')
        self.ui_manager.draw_ui(screen)
