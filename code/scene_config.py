from pygame_gui.core import ObjectID
from pygame_gui.elements import UITextEntryLine, UILabel, UIButton, UIPanel

from interface_manager import *
from scene_manager import *


class ConfigurationScene(Scene):
    def __init__(self, height_index: int, game):
        """
        Initialize the configuration scene.
        """
        super().__init__(height_index, game)
        self.game = game
        # Create an interface manager specific to this scene
        self.interface_manager = InterfaceManager()
        # Dictionary to store configuration data (players, holes, names)
        self.data: dict = self.default_data_dictionary()
        # References for text input fields
        self.players_input: UITextEntryLine = None
        self.holes_input: UITextEntryLine = None
        self.names_fields: list[UITextEntryLine] = []
        # Panel that will contain the dynamic name fields
        self.names_fields_panel: UIPanel = None

        # Build all panels for configuration
        self.build_players_panel()
        self.build_holes_panel()
        self.build_names_panel()

    def on_enter(self) -> None:
        """Display the players input panel when entering the scene."""
        self.interface_manager.show_only_one("players_panel")

    def on_exit(self) -> None:
        """Hide all panels and reset all input fields when exiting the scene."""
        for key in self.interface_manager.interfaces:
            self.interface_manager.interfaces[key].hide()
        if self.players_input:
            self.players_input.set_text("")
        if self.holes_input:
            self.holes_input.set_text("")
        for field in self.names_fields:
            field.set_text("")

    # Functions for creating UI elements
    def create_panel(self, container, panel_id: str) -> UIPanel:
        """Create a panel"""
        return UIPanel(
            relative_rect=PANEL_LAYOUT,
            manager=self.ui_manager,
            container=container,
            margins=PANEL_MARGINS,
            object_id=ObjectID(class_id='panel', object_id=panel_id)
        )

    def create_panel_title(self, panel: UIPanel, text: str, object_id: str) -> UILabel:
        """Create a title for the panel"""
        return UILabel(
            text=text,
            manager=self.ui_manager,
            container=panel,
            relative_rect=pygame.Rect((0, 0, PANEL_WIDTH, 50)),
            anchors={'top': 'top', 'centerx': 'centerx'},
            object_id=ObjectID(class_id='label_black', object_id=object_id)
        )

    def create_next_button(self, panel: UIPanel, text: str, object_id: str) -> UIButton:
        """Create the 'Next' button"""
        # Position button above the bottom
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
        """Create the 'Previous' button"""
        # Position button at the bottom
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

    # --- Panel construction methods ---
    def build_players_panel(self) -> None:
        """Build the panel for the number of players."""
        panel = self.create_panel(self.ui_container, "#players_panel")
        # Create the title label for the panel
        self.create_panel_title(panel, "Saisissez le nombre\n\nde joueurs\n\n(5 max.)", "#players_label")
        # Create navigation buttons
        self.create_previous_button(panel, "Retour au menu", "#players_previous")
        self.create_next_button(panel, "Suivant", "#players_next")
        # Create the input for number of players
        self.players_input = UITextEntryLine(
            relative_rect=pygame.Rect((0, 0, INPUT_WIDTH, INPUT_HEIGHT)),
            placeholder_text="Nombre de joueurs",
            manager=self.ui_manager,
            container=panel,
            anchors={'center': 'center'},
            object_id=ObjectID(class_id='text_input', object_id='#players_input')
        )
        self.players_input.set_allowed_characters("numbers")
        # Add the panel to the interface manager
        self.interface_manager.add("players_panel", panel)

    def build_holes_panel(self) -> None:
        """Build the panel for the number of holes."""
        panel = self.create_panel(self.ui_container, "#holes_panel")
        self.create_panel_title(panel, "Saisissez le nombre de trous (5 max.)", "#holes_label")
        self.create_previous_button(panel, "Précédent", "#holes_previous")
        self.create_next_button(panel, "Suivant", "#holes_next")
        # Create the text input for number of holes
        self.holes_input = UITextEntryLine(
            relative_rect=pygame.Rect((0, 0, INPUT_WIDTH, INPUT_HEIGHT)),
            placeholder_text="Nombre de trous",
            manager=self.ui_manager,
            container=panel,
            anchors={'center': 'center'},
            object_id=ObjectID(class_id='text_input', object_id='#holes_input')
        )
        self.holes_input.set_allowed_characters("numbers")
        self.interface_manager.add("holes_panel", panel)

    def build_names_panel(self) -> None:
        """Build the panel for the players' names."""
        panel = self.create_panel(self.ui_container, "#names_fields_panel")
        self.create_panel_title(panel, "Saisissez les noms des joueurs", "#names_label")
        self.create_previous_button(panel, "Précédent", "#names_previous")
        self.create_next_button(panel, "Lancer", "#names_next")
        # Store the panel to add name fields dynamically later
        self.names_fields_panel = panel
        self.interface_manager.add("names_fields_panel", panel)

    # Event handling
    def process_event(self, event: pygame.event.Event) -> None:
        """Process button press events and route them to the proper handlers."""
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            ids = event.ui_element.get_object_ids()

            if "#players_next" in ids:
                self.handle_players_next()
            elif "#players_previous" in ids:
                self.scene_manager.change("start_menu_scene")
            elif "#holes_next" in ids:
                self.handle_holes_next()
            elif "#holes_previous" in ids:
                # Show the players panel when pressing "Previous" on holes panel
                self.interface_manager.show_only_one("players_panel")
            elif "#names_next" in ids:
                self.handle_names_next()
            elif "#names_previous" in ids:
                # Return to the holes panel from names panel
                self.interface_manager.show_only_one("holes_panel")

    def handle_players_next(self) -> None:
        """Handle the 'Next' button in the players panel."""
        try:
            # Convert the input text to an integer and validate it
            num_players = int(self.players_input.get_text())
            if not (1 <= num_players <= 5):
                raise ValueError
        except ValueError:
            self.game.manage_error("Nombre de joueurs invalide. Veuillez entrer un entier entre 1 et 5.")
            return
        self.data['players'] = num_players
        # Show the holes panel after successful validation
        self.interface_manager.show_only_one("holes_panel")

    def handle_holes_next(self) -> None:
        """Handle the 'Next' button in the holes panel."""
        try:
            num_holes = int(self.holes_input.get_text())
            if not (1 <= num_holes <= 5):
                raise ValueError
        except ValueError:
            self.game.manage_error("Nombre de trous invalide. Veuillez entrer un entier entre 1 et 5.")
            return
        self.data['holes'] = num_holes
        # Prepare the dynamic name fields based on the number of players entered earlier
        self.prepare_names_fields(self.data['players'])
        # Show the names panel
        self.interface_manager.show_only_one("names_fields_panel")

    def handle_names_next(self) -> None:
        """Handle the 'Launch' button in the names panel."""
        names = []
        # Iterate through each name field and collect the text
        for field in self.names_fields:
            name = field.get_text()
            if name == "":
                self.game.manage_error("Veuillez remplir tous les noms.")
                return
            names.append(name)
        self.data['names'] = names
        # After collecting names, start the game
        self.start_game()

    # Data preparation
    def default_data_dictionary(self) -> dict:
        """Return the default configuration dictionary."""
        return {"players": 1, "holes": 1, "names": []}

    def delete_names_fields(self):
        """Remove all existing player name input fields."""
        for field in self.names_fields:
            field.kill()
        self.names_fields = []

    def create_names_fields(self, num_players: int, first_field_pos: int, gap: int):
        """Create and add player name input fields to the scene."""
        for i in range(num_players):
            field = UITextEntryLine(
                relative_rect=pygame.Rect((
                    0,
                    first_field_pos + i * (INPUT_HEIGHT + gap),  # Position each field with a gap between them
                    INPUT_WIDTH,
                    INPUT_HEIGHT
                )),
                anchors={"centerx": "centerx"},
                placeholder_text=f"Nom joueur n°{i + 1}",
                manager=self.ui_manager,
                container=self.names_fields_panel,
                object_id=ObjectID(class_id='text_input', object_id=f'#name_input_{i}')
            )
            self.names_fields.append(field)

    def prepare_names_fields(self, num_players: int) -> None:
        """Prepare and dynamically create input fields for player names."""
        # Gap between each input field
        gap = INPUTS_GAP // 2
        # Total height needed for all input fields
        fields_height = INPUT_HEIGHT * num_players + gap * (num_players - 1)
        # Starting "y-coordinate" so that fields are vertically centered
        first_field_pos = (PANEL_HEIGHT - fields_height - (PANEL_MARGINS["top"] * 2)) // 2
        # Remove existing name fields before creating new ones
        self.delete_names_fields()
        # Create new name fields
        self.create_names_fields(num_players, first_field_pos, gap)

    def start_game(self) -> None:
        """Tmp method"""
        print("Données de configuration de partie :", self.data)
        self.game.game_info = self.data
        print("Info Transmise")
        self.scene_manager.change("play_scene")
        print("Scene affichée")

    def draw(self, screen) -> None:
        """Draw the scene background"""
        screen.blit(SCENE_BG_IMAGE, (0, 0))

    def update(self, dt: int) -> None:
        """Update UI components"""
        self.players_input.update(dt)
        self.holes_input.update(dt)
        for name_field in self.names_fields:
            name_field.update(dt)
