from pygame_gui.elements import UILabel, UIButton, UIPanel, UITextEntryLine as UITextField
from pygame_gui.core import ObjectID
from interface_manager import InterfaceManager
from scene_manager import Scene
from settings import *


class ConfigurationScene(Scene):
    def __init__(self, height_index: int, game):
        """
        Initialize the configuration scene.
        """
        super().__init__(height_index, game)
        self.game = game
        self.interface_manager = InterfaceManager()
        self.data: dict = self.default_game_infos_dict()
        self.names_fields: list[UITextField] = []
        self.names_fields_panel: UIPanel = None

        self.build_players_number_panel()
        self.build_holes_number_panel()
        self.build_names_panel()

    def on_enter(self) -> None:
        self.interface_manager.show_only_one("players_number_panel")

    def on_exit(self) -> None:
        for key in self.interface_manager.interfaces:
            self.interface_manager.interfaces[key].hide()
        for field in self.names_fields:
            field.set_text("")

    def create_panel(self, container, panel_id: str) -> UIPanel:
        return UIPanel(
            relative_rect=PANEL_LAYOUT,
            manager=self.ui_manager,
            container=container,
            margins=PANEL_MARGINS,
            object_id=ObjectID(class_id='panel', object_id=panel_id)
        )

    def create_title(self, panel: UIPanel, text: str, object_id: str) -> UILabel:
        return UILabel(
            text=text,
            manager=self.ui_manager,
            container=panel,
            relative_rect=pygame.Rect((0, 0), (-1, -1)),
            anchors={'top': 'top', 'centerx': 'centerx'},
            object_id=ObjectID(class_id='label_black', object_id=object_id)
        )

    def create_next_button(self, panel: UIPanel, text: str, object_id: str) -> UIButton:
        rect = pygame.Rect((0, -(INPUT_HEIGHT * 2 + INPUTS_GAP), INPUT_WIDTH, INPUT_HEIGHT))
        anchors = {'top': 'bottom', 'centerx': 'centerx'}
        return UIButton(
            relative_rect=rect,
            text=text,
            manager=self.ui_manager,
            container=panel,
            anchors=anchors,
            object_id=ObjectID(class_id='button_primary', object_id=object_id)
        )

    def create_previous_button(self, panel: UIPanel, text: str, object_id: str) -> UIButton:
        rect = pygame.Rect((0, -INPUT_HEIGHT, INPUT_WIDTH, INPUT_HEIGHT))
        anchors = {'top': 'bottom', 'centerx': 'centerx'}
        return UIButton(
            relative_rect=rect,
            text=text,
            manager=self.ui_manager,
            container=panel,
            anchors=anchors,
            object_id=ObjectID(class_id='button_secondary', object_id=object_id)
        )

    def build_players_number_panel(self) -> None:
        panel = self.create_panel(self.ui_container, "#players_number_panel")
        self.create_title(panel, "Nombre de joueurs (5 max.)", "#players_number_label")
        self.create_previous_button(panel, "Retour au menu", "#players_number_previous")

        total_buttons_height = MAX_PLAYERS_NUMBER * (INPUT_HEIGHT + INPUTS_GAP) - INPUTS_GAP
        first_button_offset = (PANEL_HEIGHT - total_buttons_height - (PANEL_MARGINS["top"] * 2)) // 2

        for i in range(1, MAX_PLAYERS_NUMBER + 1):
            if i == 1 :
                button_label = f"{i} joueur"
            else :
                button_label = f"{i} joueurs"
            button_y = first_button_offset + (i - 1) * (INPUT_HEIGHT + INPUTS_GAP)
            UIButton(
                relative_rect=pygame.Rect((0, button_y, INPUT_WIDTH, INPUT_HEIGHT)),
                text=button_label,
                manager=self.ui_manager,
                container=panel,
                anchors={'centerx': 'centerx'},
                object_id=ObjectID(class_id='button_primary', object_id=f'#players_number_btn_{i}')
            )

        self.interface_manager.add("players_number_panel", panel)

    def build_holes_number_panel(self) -> None:
        panel = self.create_panel(self.ui_container, "#holes_number_panel")
        self.create_title(panel, "Nombre de trous (5 max.)", "#holes_number_label")
        self.create_previous_button(panel, "Précédent", "#holes_number_previous")

        total_buttons_height = MAX_HOLES_NUMBER * (INPUT_HEIGHT + INPUTS_GAP) - INPUTS_GAP
        first_button_offset = (PANEL_HEIGHT - total_buttons_height - (PANEL_MARGINS["top"] * 2)) // 2

        for i in range(1, MAX_HOLES_NUMBER + 1):
            if i == 1 :
                button_label = f"{i} trou"
            else :
                button_label = f"{i} trous"
            button_y = first_button_offset + (i - 1) * (INPUT_HEIGHT + INPUTS_GAP)
            UIButton(
                relative_rect=pygame.Rect((0, button_y, INPUT_WIDTH, INPUT_HEIGHT)),
                text=button_label,
                manager=self.ui_manager,
                container=panel,
                anchors={'centerx': 'centerx'},
                object_id=ObjectID(class_id='button_primary', object_id=f'#holes_number_btn_{i}')
            )

        self.interface_manager.add("holes_number_panel", panel)

    def build_names_panel(self) -> None:
        panel : UIPanel = self.create_panel(self.ui_container, "#names_fields_panel")
        self.create_title(panel, "Saisissez les noms des joueurs", "#names_label")
        self.create_previous_button(panel, "Précédent", "#names_previous")
        self.create_next_button(panel, "Lancer", "#names_next")
        self.names_fields_panel = panel
        self.interface_manager.add("names_fields_panel", panel)

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            ids = event.ui_element.get_object_ids()
            if ids :
                for btn_id in ids:
                    if "#players_number_btn_" in btn_id:
                        btn_value = int(btn_id[-1])
                        self.handle_players_number_btn(btn_value)
                        return
                    elif "#holes_number_btn_" in btn_id:
                        btn_value = int(btn_id[-1])
                        self.handle_holes_number_btn(btn_value)
                        return
                if "#players_number_previous" in ids:
                    self.scene_manager.change("start_menu_scene")
                elif "#holes_number_previous" in ids:
                    self.interface_manager.show_only_one("players_number_panel")
                elif "#names_next" in ids:
                    self.handle_names_next()
                elif "#names_previous" in ids:
                    self.interface_manager.show_only_one("holes_number_panel")
        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            field = event.ui_element
            if field in self.names_fields:
                i = self.names_fields.index(field)
                for name_field in self.names_fields:
                    name_field.unfocus()
                if i < len(self.names_fields) - 1:
                    self.names_fields[i + 1].focus()
                else:
                    self.handle_names_next()


    def handle_players_number_btn(self, btn_value: int) -> None:
        if not (1 <= btn_value <= MAX_PLAYERS_NUMBER):
            self.game.manage_error("Nombre de joueurs invalide. Veuillez sélectionner un entier entre 1 et 5.")
            return
        self.data['players'] = btn_value
        self.interface_manager.show_only_one("holes_number_panel")

    def handle_holes_number_btn(self, btn_value: int) -> None:
        if not (1 <= btn_value <= MAX_PLAYERS_NUMBER):
            self.game.manage_error("Nombre de trous invalide. Veuillez sélectionner un entier entre 1 et 5.")
            return
        self.data['holes'] = btn_value
        self.prepare_names_fields(self.data['players'])
        self.interface_manager.show_only_one("names_fields_panel")

    def handle_names_next(self) -> None:
        names : list[str] = []
        for field in self.names_fields:
            name = field.get_text()
            if name == "":
                self.game.manage_error("Veuillez remplir tous les noms.")
                return
            elif name in names:
                self.game.manage_error("Noms saisies invalides. Les noms doivent être unique.")
                return
            elif len(name) > MAX_PLAYER_NAME_LEN:
                self.game.manage_error(f"Noms saisies invalides. Un noms ne doit pas dépasser {MAX_PLAYER_NAME_LEN} caractères.")
                return
            else :
                names.append(str(name))

        self.data['names'] = names
        self.start_game()

    def default_game_infos_dict(self) -> dict:
        return DEFAULT_GAME_DICTIONARY

    def delete_names_fields(self) -> None:
        for field in self.names_fields:
            field.kill()
        self.names_fields : list[UITextField] = []

    def create_names_fields(self, players_number: int, first_field_offset: int, gap: int) -> None:
        for i in range(players_number):
            field_y = first_field_offset + i * (INPUT_HEIGHT + gap)
            field = UITextField(
                relative_rect=pygame.Rect((0, field_y, INPUT_WIDTH, INPUT_HEIGHT)),
                anchors={"centerx": "centerx"},
                placeholder_text=f"Nom joueur n°{i + 1}",
                manager=self.ui_manager,
                container=self.names_fields_panel,
                object_id=ObjectID(class_id='text_input', object_id=f'#name_input_{i}')
            )
            field.set_text_length_limit(MAX_PLAYER_NAME_LEN)
            if i == 0 :
                field.focus()
            self.names_fields.append(field)

    def prepare_names_fields(self, players_number: int) -> None:
        fields_height = INPUT_HEIGHT * players_number + INPUTS_GAP * (players_number - 1)
        first_field_offset = (PANEL_HEIGHT - fields_height - (PANEL_MARGINS["top"] * 2)) // 2
        self.delete_names_fields()
        self.create_names_fields(players_number, first_field_offset, INPUTS_GAP)

    def start_game(self) -> None:
        print("Données de configuration de partie :", self.data)
        self.game.game_info = self.data
        self.scene_manager.change("play_scene")

    def draw(self, screen : pygame.surface.Surface) -> None:
        screen.blit(SCENE_BG_IMAGE, (0, 0))

    def update(self, dt: int) -> None:
        for name_field in self.names_fields:
            name_field.update(dt)
