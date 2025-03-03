from settings import *
from pygame_gui.elements.ui_panel import UIPanel
from pygame_gui.elements.ui_button import UIButton
from pygame_gui.elements.ui_label import UILabel


class SceneManager:
    """Allows to add and manage multiple scenes."""

    def __init__(self):
        """
        Initializes the scene manager.
        """
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
                print(f"[SceneManager] Changing scene: {scene_name}")
        else:
            if DEBUG_MODE:
                print(f"[SceneManager] Unknown scene: {scene_name}")

    # Basic pygame methods ---
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

    # Basic methods to create a scene---
    def process_event(self, event):
        """
        Processes an event.
        :param event: The event to process.
        :type event : pygame.event.Event
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



