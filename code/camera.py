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

    def getAbsoluteCoord(self, screen_coord):
        """Convertit une coordonnée à l'écran en coordonnée sur la carte."""
        center_x = self.screen.get_width() / 2
        center_y = self.screen.get_height() / 2
        world_x = self.offset_X + (screen_coord[0] - center_x) / self.zoom_factor
        world_y = self.offset_Y + (screen_coord[1] - center_y) / self.zoom_factor
        return world_x, world_y

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
        # Récupérer les coordonnées du centre de l'écran
        center_x = WINDOW_WIDTH / 2
        center_y = WINDOW_HEIGHT / 2

        # Appliquer le zoom et le décalage de la caméra
        screen_x = center_x + (world_x - self.offset_X - center_x) * self.zoom_factor
        screen_y = center_y + (world_y - self.offset_Y - center_y) * self.zoom_factor

        return screen_x, screen_y

    def is_position_on_screen(self,x:int,y:int) -> bool:
        if x < 0 or x > WINDOW_WIDTH:
            return False
        elif y < 0 or y > WINDOW_HEIGHT:
            return False
        else:
            return True

    def is_world_position_on_screen(self,world_x:int,world_y:int):
        x,y = self.world_to_screen(world_x,world_y)
        return self.is_position_on_screen(x,y)