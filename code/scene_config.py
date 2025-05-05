from pygame_gui.elements import UILabel, UIButton, UIPanel, UITextEntryLine as UITextField
from pygame_gui.core import ObjectID
from interface_manager import InterfaceManager
from scene_manager import Scene
from settings import *


class ConfigurationScene(Scene):
    def __init__(self, height_index: int, game):
        """
        Scène de configuration d'une partie de golf, divisée en plusieurs étapes :
        1. Sélection du nombre de joueurs
        2. Sélection du nombre de trous
        3. Saisie des noms des joueurs

        Fonctionnalités :
        - Si 1 joueur est sélectionné, la saisie des noms n'est pas demandée. Par défaut le nom est "Vous".
        - Lors de la saisie, "Entrée" permet de passer au champ suivant ; sur le dernier, la partie démarre.
        - Les saisies sont sécurisées : tous les noms doivent être complétés et uniques.
        """

        super().__init__(height_index, game)
        self.game = game
        self.interface_manager = InterfaceManager()
        self.data: dict = DEFAULT_GAME_DICTIONARY
        self.names_fields: list[UITextField] = []
        self.names_fields_panel: UIPanel = None

        self.build_players_number_panel()
        self.build_holes_number_panel()
        self.build_names_panel()

    def on_enter(self) -> None:
        # Par défaut, on affiche l'interface pour sélectionner le nombre de joueurs.
        self.interface_manager.show_only_one("players_number_panel")

    def on_exit(self) -> None:
        # En quittant la scène, on cache toutes les interfaces.
        self.interface_manager.hide_all()

    def create_panel(self, container, panel_id: str) -> UIPanel:
        # Création d'un panel générique correspondant à une étape
        return UIPanel(
            relative_rect=PANEL_LAYOUT,
            manager=self.ui_manager,
            container=container,
            margins=PANEL_MARGINS,
            object_id=ObjectID(class_id='panel', object_id=panel_id)
        )

    def create_title(self, panel: UIPanel, text: str, object_id: str) -> UILabel:
        # Création d'un texte de titre générique.
        return UILabel(
            text=text,
            manager=self.ui_manager,
            container=panel,
            relative_rect=pygame.Rect((0, 0), (PANEL_WIDTH, -1)),
            anchors={'top': 'top', 'centerx': 'centerx'},
            object_id=ObjectID(class_id='label_black', object_id=object_id)
        )

    def create_next_button(self, panel: UIPanel, text: str, object_id: str) -> UIButton:
        # Création d'un bouton générique pour passer à l'étape suivante.
        # Il est positionné en bas, au centre, au-dessus du bouton précédent
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
        # Création d'un bouton générique pour revenir à l'étape précédente.
        # Il est positionné en bas, au centre, en dessous du bouton suivant
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
        # Création du panel de séléction du nombre de joueurs.
        panel = self.create_panel(self.ui_container, "#players_number_panel")
        self.create_title(panel, "Nombre de joueurs (5 max.)", "#players_number_label")
        self.create_previous_button(panel, "Retour au menu", "#players_number_previous")

        # Pour permettre le choix, on crée X boutons associés à un nombre de joueurs.
        # On calcule la position du premier bouton sur le panel.
        total_buttons_height = MAX_PLAYERS_NUMBER * (INPUT_HEIGHT + INPUTS_GAP) - INPUTS_GAP
        first_button_offset = (PANEL_HEIGHT - total_buttons_height - (PANEL_MARGINS["top"] * 2)) // 2

        # On crée les boutons les un en dessous des autres avec les bons labels.
        for i in range(1, MAX_PLAYERS_NUMBER + 1):
            if i == 1:
                button_label = f"{i} joueur"
            else:
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
        # Création du panel de séléction du nombre de trous.
        panel = self.create_panel(self.ui_container, "#holes_number_panel")
        self.create_title(panel, "Nombre de trous (5 max.)", "#holes_number_label")
        self.create_previous_button(panel, "Précédent", "#holes_number_previous")

        # Pour permettre le choix, on crée X boutons associés à un nombre de trous.
        # On calcule la position du premier bouton sur le panel.
        total_buttons_height = MAX_HOLES_NUMBER * (INPUT_HEIGHT + INPUTS_GAP) - INPUTS_GAP
        first_button_offset = (PANEL_HEIGHT - total_buttons_height - (PANEL_MARGINS["top"] * 2)) // 2

        # On crée les boutons les un en dessous des autres avec les bons labels.
        for i in range(1, MAX_HOLES_NUMBER + 1):
            if i == 1:
                button_label = f"{i} trou"
            else:
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
        # Création du panel de saisie des noms des joueurs.
        panel: UIPanel = self.create_panel(self.ui_container, "#names_fields_panel")
        self.create_title(panel, "Saisissez les noms des joueurs", "#names_label")
        self.create_previous_button(panel, "Précédent", "#names_previous")
        self.create_next_button(panel, "Lancer", "#names_next")
        # Selon le nombre de joueurs sélectionné à la première étape, on doit créer X champs.
        # On stocke donc le panel pour créer et afficher les champs plus tard.
        self.names_fields_panel = panel

        self.interface_manager.add("names_fields_panel", panel)

    def process_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            # Si un bouton est cliqué, on récupère son id.
            ids = event.ui_element.get_object_ids()
            if ids:
                for btn_id in ids:
                    if "#players_number_btn_" in btn_id:
                        # Gère le clic sur un bouton de sélection du nombre de joueurs
                        btn_value = int(btn_id[-1])
                        self.handle_players_number_btn(btn_value)
                        return
                    elif "#holes_number_btn_" in btn_id:
                        # Gère le clic sur un bouton de sélection du nombre de trous
                        btn_value = int(btn_id[-1])
                        self.handle_holes_number_btn(btn_value)
                        return
                # Gestion de la navigation entre les différentes étapes
                if "#players_number_previous" in ids:
                    self.scene_manager.change("start_menu_scene")
                elif "#holes_number_previous" in ids:
                    self.interface_manager.show_only_one("players_number_panel")
                elif "#names_next" in ids:
                    self.handle_names_next()
                elif "#names_previous" in ids:
                    self.interface_manager.show_only_one("holes_number_panel")

        elif event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED:
            # Gestions des raccourcis clavier lors de la saisie des noms des joueurs :
            # L'utilisateur peut cliquer sur "Enter" pour passer au champ suivant.
            field = event.ui_element  # On récupère le champ concerné
            if field in self.names_fields:
                # On récupère son indice dans la liste des champs
                i = self.names_fields.index(field)
                # On désélectionne tous les champs
                for name_field in self.names_fields:
                    name_field.unfocus()
                if i < len(self.names_fields) - 1:
                    # Si ce n'est pas le dernier
                    # On sélectionne le champ suivant dans la liste
                    self.names_fields[i + 1].focus()
                else:
                    # Sinon, on passe à l'étape suivante : le lancement du jeu.
                    self.handle_names_next()

    def handle_players_number_btn(self, btn_value: int) -> None:
        if not (1 <= btn_value <= MAX_PLAYERS_NUMBER):
            self.game.manage_error("Nombre de joueurs invalide. Veuillez sélectionner un entier entre 1 et 5.")
            return
        # Si le nombre de joueurs est valide :
        # On stocke cette valeur et on passe à l'étape suivante.
        self.data["players"] = btn_value
        self.interface_manager.show_only_one("holes_number_panel")

    def handle_holes_number_btn(self, btn_value: int) -> None:
        if not (1 <= btn_value <= MAX_PLAYERS_NUMBER):
            self.game.manage_error("Nombre de trous invalide. Veuillez sélectionner un entier entre 1 et 5.")
            return
        # Si le nombre de joueurs est valide :
        # On stocke cette valeur
        self.data["holes"] = btn_value
        if self.data["players"] == 1:
            # S'il n'y a qu'un joueur, on ne demande pas la saisie des noms.
            # On met un nom par défaut et on lance le jeu.
            self.data["names"] = ["Vous"]
            self.start_game()
        else:
            # On crée les champs de saisie des noms des joueurs et on passe à l'étape suivante.
            self.prepare_names_fields(self.data["players"])
            self.interface_manager.show_only_one("names_fields_panel")

    def handle_names_next(self) -> None:
        names: list[str] = []
        for field in self.names_fields:
            # On récupère le texte du champ
            name = field.get_text()
            if name == "":
                # On vérifie s'il n'est pas vide
                self.game.manage_error("Veuillez remplir tous les noms.")
                return
            elif name in names:
                # On vérifie si la saisie n'est pas déja utilisée
                self.game.manage_error("Noms saisies invalides. Les noms doivent être unique.")
                return
            elif len(name) > MAX_PLAYER_NAME_LEN:
                # On vérifie s'il n'est pas trop long
                self.game.manage_error(
                    f"Noms saisies invalides. Un noms ne doit pas dépasser {MAX_PLAYER_NAME_LEN} caractères.")
                return
            else:
                names.append(str(name))

        # Si le nombre de joueurs est valide, on stocke cette valeur et on lance le jeu :).
        self.data['names'] = names
        self.start_game()

    def delete_names_fields(self) -> None:
        for field in self.names_fields:
            field.kill()
        self.names_fields: list[UITextField] = []

    def create_names_fields(self, players_number: int, first_field_offset: int, gap: int) -> None:
        # Création des champs pour la saisie des noms des joueurs
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
            # On fix la longueur max de la saisie
            field.set_text_length_limit(MAX_PLAYER_NAME_LEN)
            self.names_fields.append(field)

    def prepare_names_fields(self, players_number: int) -> None:
        # On calcule la position du premier champ sur le panel.
        fields_height = INPUT_HEIGHT * players_number + INPUTS_GAP * (players_number - 1)
        first_field_offset = (PANEL_HEIGHT - fields_height - (PANEL_MARGINS["top"] * 2)) // 2
        # On supprime les anciens champs et on en recrée
        self.delete_names_fields()
        self.create_names_fields(players_number, first_field_offset, INPUTS_GAP)

    def start_game(self) -> None:
        if DEBUG_MODE:
            print("Données de configuration de partie :", self.data)
        self.game.game_info = self.data
        self.scene_manager.change("play_scene")

    def draw(self, screen: pygame.surface.Surface) -> None:
        screen.blit(SCENE_BG_IMAGE, (0, 0))

    def update(self, dt: int) -> None:
        for name_field in self.names_fields:
            # Juste pour faire clignoter le curseur lors de la saisie utilisateur
            name_field.update(dt)
