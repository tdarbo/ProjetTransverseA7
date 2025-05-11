from settings import *


class InterfaceManager:
    """
    Interface manager to handle multiple instances of Interface.
    Allows adding, removing, showing, hiding, and toggling interfaces.
    """

    def __init__(self):
        self.interfaces: dict = dict()  # Dictionary of interfaces by identifier

    def add(self, interface_name, interface):
        """
        Adds an interface to the manager.

        :param interface_name: Identifier of the interface.
        :param interface: Instance of Menu.
        """
        self.interfaces[interface_name] = interface

        if DEBUG_MODE:
            print(f"[InterfaceManager] Interface {interface_name} added to the interface list.")

    def remove(self, interface_name):
        """
        Removes and destroys an interface.

        :param interface_name: Identifier of the interface to remove.
        """
        if interface_name in self.interfaces:
            self.interfaces[interface_name].kill()  # Destroys the UI panel
            del self.interfaces[interface_name]

            if DEBUG_MODE:
                print(f"[InterfaceManager] Interface {interface_name} removed.")

    def show(self, interface_name):
        """
        Shows the identified interface.

        :param interface_name: Identifier of the interface to show.
        """
        if interface_name in self.interfaces:
            self.interfaces[interface_name].show()

    def show_only_one(self, interface_name):
        """
        Shows only the identified interface. The others are hidden

        :param interface_name: Identifier of the interface to show.
        """
        for interface in self.interfaces.keys():
            self.interfaces[interface].hide()
        self.interfaces[interface_name].show()

    def hide_all(self):
        # Hide all interfaces
        for interface in self.interfaces.keys():
            self.interfaces[interface].hide()

    def hide(self, interface_name):
        """
        Hides the identified interface.

        :param interface_name: Identifier of the interface to hide.
        """
        if interface_name in self.interfaces:
            self.interfaces[interface_name].hide()

    def toggle(self, interface_name):
        """
        Toggles the visibility of the identified interface.

        :param interface_name: Identifier of the interface to toggle.
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
