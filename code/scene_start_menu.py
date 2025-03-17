from pygame_gui.core import ObjectID  # Import de la classe ObjectID

from scene_manager import *


class StartMenuScene(Scene):
    def __init__(self, height_index, game):
        """
        Initialise la scène du menu principal.
        """
        super().__init__(height_index, game)
        self.build_main_menu_panel()

    def build_main_menu_panel(self):
        """
        Construit les éléments d'interface du menu principal.
        """
        n_elements = 5
        elements_height = INPUT_HEIGHT * n_elements + INPUTS_GAP * (n_elements - 1)
        first_element_height = (PANEL_HEIGHT - elements_height - (PANEL_MARGINS["top"] * 2)) // 2

        panel = pygame_gui.elements.UIPanel(
            relative_rect=PANEL_LAYOUT,
            manager=self.ui_manager,
            container=self.ui_container,  # Container principal de la scène
            margins=PANEL_MARGINS,
            object_id=ObjectID(class_id='panel', object_id='#main_menu_panel')
        )
        game_name_label = pygame_gui.elements.UILabel(
            text=GAME_NAME,
            manager=self.ui_manager,
            container=panel,
            relative_rect=pygame.Rect((0, first_element_height, -1, INPUT_HEIGHT)),
            anchors={'centerx': 'centerx'},
            object_id=ObjectID(class_id='label_big_black', object_id='#main_menu_game_name')
        )
        play_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, INPUTS_GAP), (INPUT_WIDTH, INPUT_HEIGHT)),
            text='Play',
            manager=self.ui_manager,
            container=panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': game_name_label
            },
            object_id=ObjectID(class_id='button_primary', object_id='#main_menu_play_btn')
        )
        rules_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, INPUTS_GAP), (INPUT_WIDTH, INPUT_HEIGHT)),
            text='Rules',
            manager=self.ui_manager,
            container=panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': play_btn
            },
            object_id=ObjectID(class_id='button_primary', object_id='#main_menu_rules_btn')
        )
        settings_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, INPUTS_GAP), (INPUT_WIDTH, INPUT_HEIGHT)),
            text='Settings',
            manager=self.ui_manager,
            container=panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': rules_btn
            },
            object_id=ObjectID(class_id='button_primary', object_id='#main_menu_settings_btn')
        )
        exit_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, INPUTS_GAP), (INPUT_WIDTH, INPUT_HEIGHT)),
            text='Exit',
            manager=self.ui_manager,
            container=panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': settings_btn
            },
            object_id=ObjectID(class_id='button_secondary', object_id='#main_menu_exit_btn')
        )

        if DEBUG_MODE:
            print(f"[{self.__class__.__name__}] Main menu UI created.")

    def process_event(self, event):
        """
        Traite les événements de la scène.
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            ids = event.ui_element.get_object_ids()
            # On vérifie l'identifiant unique (object_id) pour traiter l'événement
            if "#main_menu_play_btn" in ids:
                if DEBUG_MODE:
                    print("Play button pressed.")
                self.scene_manager.change("config_scene")
            elif "#main_menu_rules_btn" in ids:
                if DEBUG_MODE:
                    print("Rules button pressed.")
            elif "#main_menu_settings_btn" in ids:
                if DEBUG_MODE:
                    print("Settings button pressed.")
            elif "#main_menu_exit_btn" in ids:
                if DEBUG_MODE:
                    print("Exit button pressed.")
                self.game.running = False

    def draw(self, screen):
        """
        Dessine la scène.
        """
        screen.fill('red')
        screen.blit(SCENE_BG_IMAGE, (0, 0))
