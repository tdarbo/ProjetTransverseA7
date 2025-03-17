from scene_manager import *


class ComponentsScene(Scene):
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
        panel = pygame_gui.elements.UIPanel(
            relative_rect=PANEL_LAYOUT,
            manager=self.ui_manager,
            container=self.ui_container,  # Container principal de la scene
            margins=PANEL_MARGINS,
        )
        label_small = pygame_gui.elements.UILabel(
            text="This is a small label, 1, 2, 3, ...",
            manager=self.ui_manager,
            container=panel,
            relative_rect=pygame.Rect((0, 0, -1, -1)),
            anchors={'centerx': 'centerx'},
            object_id="label_small_black"
        )
        label = pygame_gui.elements.UILabel(
            text="This is a small label, 1, 2, 3, ...",
            manager=self.ui_manager,
            container=panel,
            relative_rect=pygame.Rect((0, 20, -1, -1)),
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': label_small
            },
            object_id="label_black",
        )
        label_medium = pygame_gui.elements.UILabel(
            text="This is a medium label",
            manager=self.ui_manager,
            container=panel,
            relative_rect=pygame.Rect((0, 20, -1, -1)),
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': label
            },
            object_id="label_medium_black"
        )
        label_large = pygame_gui.elements.UILabel(
            text="This is a large label",
            manager=self.ui_manager,
            container=panel,
            relative_rect=pygame.Rect((0, 20, -1, -1)),
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': label_medium
            },
            object_id="label_large_black"
        )
        label_big = pygame_gui.elements.UILabel(
            text="This is a big label",
            manager=self.ui_manager,
            container=panel,
            relative_rect=pygame.Rect((0, 20, -1, -1)),
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': label_large
            },
            object_id="label_big_black"
        )
        primary_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 20, INPUT_WIDTH, INPUT_HEIGHT)),
            text='Primary',
            manager=self.ui_manager,
            container=panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': label_big
            },
            object_id="button_primary"
        )
        secondary_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, 20, INPUT_WIDTH, INPUT_HEIGHT)),
            text='Secondary',
            manager=self.ui_manager,
            container=panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': primary_btn
            },
            object_id="button_secondary"
        )
        text_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((0, 20, INPUT_WIDTH, INPUT_HEIGHT)),
            manager=self.ui_manager,
            container=panel,
            placeholder_text="Nom joueur n°1",
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': secondary_btn
            },
            object_id="text_input"
        )

        if DEBUG_MODE:
            print(f"[{self.__class__.__name__}] Components Scene.")

    def draw(self, screen):
        """
        Dessine la scène.
        """
        screen.fill('black')
        screen.blit(SCENE_BG_IMAGE, (0, 0))
