from camera_animator import *
from settings import *
import pygame


class Camera:
    def __init__(self, screen):
        self.offset_X = 0.0
        self.offset_Y = 0.0
        self.zoom_factor = 1.0
        self.screen = screen
        self.is_dragging = False
        self.prev_mouse_pos = (0, 0)
        self.animator = CameraAnimator()

    def addZoom(self, k):
        """
        Ajuste le zoom en ajoutant k au facteur actuel.
        On limite le zoom entre MIN_ZOOM et MAX_ZOOM (def dans settings).
        """
        new_zoom = self.zoom_factor + k
        if MIN_ZOOM <= new_zoom <= MAX_ZOOM:
            self.zoom_factor = new_zoom

    def addOffset(self, dx, dy):
        """Ajuste l'offset de la caméra. On ajoute le décalage sur l'axe x et y."""
        self.offset_X -= dx / self.zoom_factor
        self.offset_Y -= dy / self.zoom_factor

    def process_event(self, event):
        """
        Met à jour la caméra en fonction des événements.
        Gère zoom (molette) et déplacement (clic droit).
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        if event.type == pygame.MOUSEBUTTONDOWN:
            # Zoom avec la molette
            if event.button == 4:  # Zoom avant
                self.addZoom(0.1)
            elif event.button == 5:  # Zoom arrière
                self.addZoom(-0.1)
            # Clic droit pour déplacer la caméra
            elif event.button == 3:
                self.is_dragging = True
                self.prev_mouse_pos = (mouse_x, mouse_y)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 3:
                self.is_dragging = False
        elif event.type == pygame.MOUSEMOTION:
            if self.is_dragging:
                current_pos = (mouse_x, mouse_y)
                dx = current_pos[0] - self.prev_mouse_pos[0]
                dy = current_pos[1] - self.prev_mouse_pos[1]
                self.addOffset(dx, dy)
                self.prev_mouse_pos = current_pos

    def resetCamera(self):
        self.offset_X = 0.0
        self.offset_Y = 0.0
        self.zoom_factor = 1.0
        self.is_dragging = False

    def world_to_screen(self, world_x, world_y):
        """
        Converts world coordinates to screen coordinates.

        Args:
            world_x, world_y: Position in world space

        Returns:
            screen_x, screen_y: Position in screen space
        """
        # Get screen center
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Calculate the screen position
        # 1. Subtract camera position to get position relative to camera
        # 2. Apply zoom
        # 3. Add screen center to position relative to screen center
        screen_x = ((world_x - self.offset_X) * self.zoom_factor) + (screen_width / 2)
        screen_y = ((world_y - self.offset_Y) * self.zoom_factor) + (screen_height / 2)

        return screen_x, screen_y

    def screen_to_world_coords(self, screen_x, screen_y):
        """
        Converts screen coordinates to world coordinates.

        Args:
            screen_x, screen_y: Position in screen space

        Returns:
            world_x, world_y: Position in world space
        """
        # Get screen center
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Calculate the world position
        # 1. Subtract screen center to get position relative to screen center
        # 2. Divide by zoom to get unscaled position
        # 3. Add camera position to get position in world space
        world_x = ((screen_x - (screen_width / 2)) / self.zoom_factor) + self.offset_X
        world_y = ((screen_y - (screen_height / 2)) / self.zoom_factor) + self.offset_Y

        return world_x, world_y

    def is_position_on_screen(self, screen_x, screen_y):
        """
        Checks if a screen position is visible.

        Args:
            screen_x, screen_y: Position in screen space

        Returns:
            bool: True if the position is on screen
        """
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        return (0 <= screen_x <= screen_width and
                0 <= screen_y <= screen_height)

    def is_world_position_on_screen(self, world_x, world_y):
        """
        Checks if a world position is visible on screen.

        Args:
            world_x, world_y: Position in world space

        Returns:
            bool: True if the position is on screen
        """
        screen_x, screen_y = self.world_to_screen(world_x, world_y)
        return self.is_position_on_screen(screen_x, screen_y)

    def screen_to_world(self, screen_coord):
        """
        Converts a screen coordinate tuple to world coordinate.

        Args:
            screen_coord: (x, y) tuple of screen position

        Returns:
            (world_x, world_y): Position in world space
        """
        return self.screen_to_world_coords(screen_coord[0], screen_coord[1])
