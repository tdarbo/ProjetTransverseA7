from settings import *


class SceneManager:
    def __init__(self):
        """
        Initialise le "gestionnaire" de scènes.

        Cette class permet d'ajouter, de changer et de gérer différentes scènes du jeu
        (menu principal, jeu, écran de fin, etc...).
        """
        self.scenes: dict = dict()  # Dictionnaire contenant les scènes
        self.current_scene = None  # Scène active

    def add(self, scene_name: str, scene):
        """
        Ajoute une nouvelle scène.

        :param scene_name: Nom unique de la scène (ex: "menu", "game", "pause").
        :param scene: Instance de la scène à ajouter.
        """
        scene.hide_ui()  # Cache l'interface de la scène au départ
        self.scenes[scene_name] = scene

    def change(self, scene_name: str):
        """
        Change la scène active en une nouvelle scène.

        :param scene_name: Nom de la scène vers laquelle passer.
        """
        if self.current_scene is not None:
            self.current_scene.hide_ui()  # Cache son interface
            self.current_scene.on_exit()  # On appelle sa fonction de sortie
            if DEBUG_MODE:
                print(f"[{self.__class__.__name__}] Exiting the current scene.")

        # On passe à la scène demandée si elle existe
        if scene_name in self.scenes:
            self.current_scene = self.scenes[scene_name]
            self.current_scene.show_ui()  # Affiche son interface
            self.current_scene.on_enter()  # On appelle sa fonction d'entrée
            if DEBUG_MODE:
                print(f"[{self.__class__.__name__}] Entering the new scene: '{scene_name}'.")
        else:
            if DEBUG_MODE:
                print(f"[{self.__class__.__name__}] Scene '{scene_name}' not found.")

    def process_event(self, event):
        """
        Transmet un event à la scène courante.

        :param event: Événement Pygame à traiter.
        """
        if self.current_scene:
            self.current_scene.process_event(event)

    def update(self, dt):
        """
        Met à jour la scène courante.

        :param dt: Temps écoulé depuis la dernière mise à jour (delta time en ms).
        """
        if self.current_scene:
            self.current_scene.update(dt)

    def draw(self, screen):
        """
        Dessine la scène courante à l'écran.

        :param screen: Surface Pygame où dessiner.
        """
        if self.current_scene:
            self.current_scene.draw(screen)


class Scene:
    def __init__(self, height_index: int, game):
        """
        Classe de base pour toutes les scènes du jeu.

        Chaque scène dispose de son propre container d'UI,
        et peut gérer ses événements.
        """
        self.game = game
        self.ui_manager = self.game.ui_manager  # Manager de l'UI (pygame_gui)
        self.scene_manager = self.game.scene_manager

        self.ui_container = pygame_gui.core.UIContainer(
            relative_rect=pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT),
            manager=self.ui_manager,
            starting_height=height_index,
            object_id="@container"
        )

    def hide_ui(self):
        """
        Cache les éléments d'interface utilisateur de la scène.
        """
        self.ui_container.hide()

    def show_ui(self):
        """
        Affiche les éléments d'interface utilisateur de la scène.
        """
        self.ui_container.show()

    def on_enter(self):
        """
        Appelé automatiquement lors de l'entrée dans la scène.
        """
        pass

    def on_exit(self):
        """
        Appelé automatiquement lors de la sortie de la scène.
        """
        pass

    def process_event(self, event):
        """
        Traite un événement (clavier, souris, etc.).

        :param event: Événement Pygame.
        """
        pass

    def update(self, dt: int):
        """
        Met à jour la logique de la scène.

        :param dt: Temps écoulé (delta time) depuis la dernière mise à jour.
        """
        pass

    def draw(self, screen):
        """
        Affiche le contenu de la scène à l’écran.

        :param screen: Surface Pygame
        """
        pass
