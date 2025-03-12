from interface_manager import *
from scene_manager import *


class PlayScene(Scene):
    def __init__(self, height_index, game):
        """
        Initialize the game scene.
        """
        super().__init__(height_index, game)

        self.build_ui()

    def build_ui(self):
        """
        Build the game UI elements.
        """
        game_name_label = pygame_gui.elements.UILabel(
            text=GAME_NAME + " Game",
            manager=self.ui_manager,
            container=self.ui_container,
            relative_rect=pygame.Rect((0, 0, -1, 30)),
            anchors={'centerx': 'centerx'},
            object_id="game_scene_game_name",
        )
        back_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 20), (300, 50)),
            text='Back',
            manager=self.ui_manager,
            container=self.ui_container,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': game_name_label
            },
            object_id="game_scene_back_btn",
        )

    def process_event(self, event):
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element.text == "Back":
                if DEBUG_MODE:
                    print(f"[{self.__class__.__name__}] Back button pressed.")
                self.scene_manager.change("start_menu_scene")

    def draw(self, screen):
        screen.fill('black')
