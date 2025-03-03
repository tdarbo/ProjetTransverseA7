from settings import *


class InterfaceManager:
    """
    Menu manager to handle multiple instances of Menu.
    Allows adding, removing, showing, hiding, and toggling menus,
    and easily transmitting events to managed menus.
    """

    def __init__(self):
        self.interfaces = {}  # Dictionary of menus by identifier

    def add(self, interface_name, menu):
        """
        Adds a menu to the manager.

        :param interface_name: Identifier of the menu.
        :type interface_name: str
        :param menu: Instance of Menu.
        :type menu: Menu
        """
        self.interfaces[interface_name] = menu

        if DEBUG_MODE:
            print(f"[InterfaceManager] Interface {interface_name} added to the menu list.")

    def remove(self, interface_name):
        """
        Removes and destroys a menu.

        :param interface_name: Identifier of the menu to remove.
        :type interface_name: str
        """
        if interface_name in self.interfaces:
            self.interfaces[interface_name].kill()  # Destroys the UI panel
            del self.interfaces[interface_name]

            if DEBUG_MODE:
                print(f"[InterfaceManager] Interface {interface_name} removed.")

    def show(self, interface_name):
        """
        Shows the identified menu.

        :param interface_name: Identifier of the menu to show.
        :type interface_name: str
        """
        if interface_name in self.interfaces:
            self.interfaces[interface_name].show()

    def hide(self, interface_name):
        """
        Hides the identified menu.

        :param interface_name: Identifier of the menu to hide.
        :type interface_name: str
        """
        if interface_name in self.interfaces:
            self.interfaces[interface_name].hide()

    def toggle(self, interface_name):
        """
        Toggles the visibility of the identified menu.

        :param interface_name: Identifier of the menu to toggle.
        :type interface_name: str
        """
        if interface_name in self.interfaces:
            if self.interfaces[interface_name].is_visible:
                self.hide(interface_name)
                if DEBUG_MODE:
                    print(f"[InterfaceManager] Interface {interface_name} hidden.")
            else:
                self.show(interface_name)
                if DEBUG_MODE:
                    print(f"[InterfaceManager] Interface {interface_name} shown.")
