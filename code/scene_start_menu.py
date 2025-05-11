from pygame_gui.core import ObjectID
from scene_manager import *
from settings import *


class StartMenuScene(Scene):
    def __init__(self, height_index, game):
        """
        Initialise la scène du menu principal.
        Elle sert de point d'entrée dans le jeu et permet d'accéder
        aux autres scènes : configuration, règles, paramètres ou quitter.
        """
        super().__init__(height_index, game)
        self.game = game
        self.build_main_menu_panel()  # Construction de l'interface du menu principal


    def build_main_menu_panel(self):
        """
        Construit les éléments d'interface du menu principal.
        Cette interface contient : le nom du jeu, et 4 boutons (Jouer, Règles, Paramètres, Quitter).
        """
        elements_number = 5  # Nombre total d'éléments empilés verticalement
        elements_height = INPUT_HEIGHT * elements_number + INPUTS_GAP * (elements_number - 1)
        first_element_offset = (PANEL_HEIGHT - elements_height - (PANEL_MARGINS["top"] * 2)) // 2

        # Création du panel principal du menu
        panel = pygame_gui.elements.UIPanel(
            relative_rect=PANEL_LAYOUT,
            manager=self.ui_manager,
            container=self.ui_container,  # Container principal de la scène
            margins=PANEL_MARGINS,
            object_id=ObjectID(class_id='panel', object_id='#main_menu_panel')
        )

        # Affichage du nom du jeu centré en haut
        game_name_label = pygame_gui.elements.UILabel(
            text=GAME_NAME,
            manager=self.ui_manager,
            container=panel,
            relative_rect=pygame.Rect((0, first_element_offset, -1, INPUT_HEIGHT)),
            anchors={'centerx': 'centerx'},
            object_id=ObjectID(class_id='label_big_black', object_id='#main_menu_game_name')
        )

        # Bouton "Jouer" placé juste sous le nom du jeu
        play_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, INPUTS_GAP), (INPUT_WIDTH, INPUT_HEIGHT)),
            text='Jouer',
            manager=self.ui_manager,
            container=panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': game_name_label  # Ancrage relatif à l’élément précédent
            },
            object_id=ObjectID(class_id='button_primary', object_id='#main_menu_play_btn')
        )

        # Bouton "Règles" positionné sous "Jouer"
        rules_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, INPUTS_GAP), (INPUT_WIDTH, INPUT_HEIGHT)),
            text='Règles',
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

        # Bouton "Paramètres" positionné sous "Règles"
        credits_btn = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, INPUTS_GAP), (INPUT_WIDTH, INPUT_HEIGHT)),
            text='Crédits',
            manager=self.ui_manager,
            container=panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': rules_btn
            },
            object_id=ObjectID(class_id='button_primary', object_id='#main_menu_credits_btn')
        )

        # Bouton "Quitter" positionné sous "Paramètres"
        pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect((0, INPUTS_GAP), (INPUT_WIDTH, INPUT_HEIGHT)),
            text='Quitter',
            manager=self.ui_manager,
            container=panel,
            anchors={
                'top': 'top',
                'bottom': 'top',
                'centerx': 'centerx',
                'top_target': credits_btn
            },
            object_id=ObjectID(class_id='button_secondary', object_id='#main_menu_exit_btn')
        )

    def process_event(self, event):
        """
        Traite les événements de la scène, notamment les clics sur les boutons du menu principal.
        """
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            ids = event.ui_element.get_object_ids()
            # Vérifie les identifiants des boutons pour réagir en conséquence
            if "#main_menu_play_btn" in ids:
                if DEBUG_MODE:
                    print("Play button pressed.")
                self.scene_manager.change("config_scene")  # Transition vers la scène de configuration
            elif "#main_menu_rules_btn" in ids:
                self.game.toggle_rules_window()  # Affiche de la fenêtre des règles
            elif "#main_menu_credits_btn" in ids:
                self.game.toggle_credits_window()  # Affiche de la fenêtre des crédits
            elif "#main_menu_exit_btn" in ids:
                self.game.running = False

    def draw(self, screen):
        """Dessine la scène."""
        screen.blit(SCENE_BG_IMAGE, (0, 0))
