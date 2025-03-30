from settings import *


class SceneManager:
    def __init__(self):
        """Responsible for switching scenes"""
        self.scenes: dict = dict()  # Dictionary of scenes by name
        self.current_scene = None  # The currently active scene

    def add(self, scene_name: str, scene):
        """
        Add a new scene to the manager.

        :param scene_name: The name of the scene.
        :param scene: The scene object to add.
        """
        scene.hide_ui()
        self.scenes[scene_name] = scene

    def change(self, scene_name: str):
        """
        Change the current scene to a new one.

        :param scene_name: The name of the scene to change to.
        """
        # If a scene is currently active, perform its cleanup
        if self.current_scene is not None:
            self.current_scene.hide_ui()
            self.current_scene.on_exit()
            if DEBUG_MODE:
                print(f"[{self.__class__.__name__}] Exiting the current scene.")

        # Switch to the new scene and initialize it
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]
            self.current_scene.show_ui()
            self.current_scene.on_enter()
            if DEBUG_MODE:
                print(f"[{self.__class__.__name__}] Entering the new scene: '{scene_name}'.")
        else:
            if DEBUG_MODE:
                print(f"[{self.__class__.__name__}] Scene '{scene_name}' not found.")

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
    def __init__(self, height_index: int, game):
        """Base class for scenes"""
        self.game = game  # Reference to the game instance
        self.ui_manager = self.game.ui_manager  # UI manager from the game
        self.scene_manager = self.game.scene_manager  # Scene manager from the game
        self.ui_container = pygame_gui.core.UIContainer(
            relative_rect=pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            manager=self.ui_manager,
            starting_height=height_index,
            object_id="@container"
        )

    def hide_ui(self):
        self.ui_container.hide()

    def show_ui(self):
        self.ui_container.show()

    def on_enter(self):
        """Called when the scene is entered."""
        pass

    def on_exit(self):
        """Called when the scene is exited."""
        pass

    def process_event(self, event):
        """
        Process an event in the scene.

        :param event: The event to process.
        """
        pass

    def update(self, dt: int):
        """
        Update the scene.

        :param dt: The time delta since the last process_event.
        """
        pass

    def draw(self, screen):
        """
        Draw the scene.

        :param screen: The screen to draw on.
        """
        pass
