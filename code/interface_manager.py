from settings import *

class InterfaceManager:
    """
    Gère plusieurs interfaces utilisateur (menus, panneaux...).
    Permet d'ajouter, retirer, afficher, cacher ou toggle leur visibilité.
    """

    def __init__(self):
        # Dictionnaire contenant les interfaces
        # Chaque interface est identifiée par son nom comme clé
        self.interfaces: dict = dict()

    def add(self, interface_name, interface):
        """
        Ajoute une interface à la liste.

        :param interface_name: Nom de l'interface (clé dans le dict).
        :param interface: Instance d'une class de pygame_gui (UIContainer, UIPanel, etc...).
        """
        self.interfaces[interface_name] = interface

        if DEBUG_MODE:
            print(f"[InterfaceManager] Interface {interface_name} added to the interface list.")

    def remove(self, interface_name):
        """
        Supprime une interface et la détruit.

        :param interface_name: Nom de l'interface à supprimer.
        """
        if interface_name in self.interfaces:
            self.interfaces[interface_name].kill()  # Appel à la méthode kill de l'interface
            del self.interfaces[interface_name]  # Suppression de l'interface dans le dictionnaire

            if DEBUG_MODE:
                print(f"[InterfaceManager] Interface {interface_name} removed.")

    def show(self, interface_name):
        """
        Affiche une interface spécifique.

        :param interface_name: Nom de l'interface à afficher.
        """
        if interface_name in self.interfaces:
            self.interfaces[interface_name].show()  # Appelle la méthode show() sur l'interface

    def show_only_one(self, interface_name):
        """
        Affiche une seule interface et cache toutes les autres.

        :param interface_name: Nom de l'interface à afficher.
        """
        for interface in self.interfaces.keys():
            self.interfaces[interface].hide()  # Cache toutes les interfaces
        self.interfaces[interface_name].show()  # Affiche seulement celle souhaitée

    def hide_all(self):
        """Cache toutes les interfaces sans exception."""
        for interface in self.interfaces.keys():
            self.interfaces[interface].hide()

    def hide(self, interface_name):
        """
        Cache une interface spécifique.

        :param interface_name: Nom de l'interface à cacher.
        """
        if interface_name in self.interfaces:
            self.interfaces[interface_name].hide()

    def toggle(self, interface_name):
        """
        Toggle l'état de visibilité d'une interface :
        si visible -> la cacher, sinon -> l'afficher.

        :param interface_name: Nom de l'interface à toggle.
        """
        if interface_name in self.interfaces:
            if self.interfaces[interface_name].visible:
                self.hide(interface_name)
                if DEBUG_MODE:
                    print(f"[InterfaceManager] Interface {interface_name} hidden.")
            else:
                self.show(interface_name)
                if DEBUG_MODE:
                    print(f"[InterfaceManager] Interface {interface_name} shown.")
