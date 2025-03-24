from camera_animator import *
from settings import *
import pygame


class Camera:
    def __init__(self,screen):
        self.offset_X = 0.0
        self.offset_Y = 0.0
        self.zoom_factor = 1.0
        self.is_dragging = False
        self.prev_mouse_x = 0
        self.prev_mouse_y = 0
        self.screen = screen
        self.animator = CameraAnimator()



        # Point de référence fixe dans le monde (100,100)
        self.ref_world_x = 100.0
        self.ref_world_y = 100.0


    def addZoom(self, k, mouse_pos):
        """
        Ajuste le zoom en utilisant un point fixe du monde (100,100) comme référence
        """

        # Mise à jour du facteur de zoom
        old_zoom = self.zoom_factor
        new_zoom = old_zoom + k

        # Limite le zoom entre 0.1x et 4x
        if not (0.5 <= new_zoom <= 4.0):
            return

        self.zoom_factor = new_zoom


    def addOffset(self, x, y):
        """
        Ajoute un décalage à la caméra en fonction des limites.
        """
        final_X = self.offset_X - x  # Inversé pour la convention
        final_Y = self.offset_Y - y  # Inversé pour la convention
        zoom = self.zoom_factor

        # Limite le déplacement
        self.offset_X = max(-2000*zoom, min(2000*zoom, final_X))
        self.offset_Y = max(-2000*zoom, min(2000*zoom, final_Y))

    def getAbsoluteCoord(self, screen_coord):
        """
        Convertit les coordonnées écran en coordonnées absolues dans le monde.

        :param screen_coord: (x, y) coordonnées sur l'écran.
        :param screen: la surface de l'écran, pour récupérer le centre.
        :return: (world_x, world_y) coordonnées dans le monde.
        """
        # Calculer le centre de l'écran
        center_x = self.screen.get_width() / 2
        center_y = self.screen.get_height() / 2

        # Inverser la transformation utilisée lors du dessin
        world_x = self.offset_X + center_x + (screen_coord[0] - center_x) / self.zoom_factor
        world_y = self.offset_Y + center_y + (screen_coord[1] - center_y) / self.zoom_factor

        return world_x, world_y

    def update(self, event):
        """
        Met à jour la caméra en fonction des événements.
        """
        mouse_x, mouse_y = pygame.mouse.get_pos()
        world_x, world_y = self.getAbsoluteCoord((mouse_x, mouse_y))

        #print(
        #    f"Mouse ({mouse_x},{mouse_y}) => ({world_x:.2f},{world_y:.2f}) | Camera offset: ({self.offset_X:.2f},{self.offset_Y:.2f}), Zoom: {self.zoom_factor:.2f}")

        if event.type == pygame.MOUSEBUTTONDOWN:
            # Molette vers le haut (Zoom avant)
            if event.button == 4:
                self.addZoom(0.1, (mouse_x, mouse_y))
            # Molette vers le bas (Zoom arrière)
            elif event.button == 5:
                self.addZoom(-0.1, (mouse_x, mouse_y))

            # Début du clic droit pour déplacer la caméra
            elif event.button == 3:
                self.is_dragging = True
                self.prev_mouse_x, self.prev_mouse_y = mouse_x, mouse_y

        elif event.type == pygame.MOUSEBUTTONUP:
            # Fin du déplacement
            if event.button == 3:
                self.is_dragging = False

        elif event.type == pygame.MOUSEMOTION:
            # Déplacement de la caméra avec le clic droit enfoncé
            if self.is_dragging:
                delta_x = mouse_x - self.prev_mouse_x
                delta_y = mouse_y - self.prev_mouse_y
                self.addOffset(delta_x, delta_y)

                # Mise à jour des coordonnées précédentes
                self.prev_mouse_x, self.prev_mouse_y = mouse_x, mouse_y


    def resetCamera(self):
        """
        Réinitialise la caméra à son état initial.
        """
        self.offset_X = 0.0
        self.offset_Y = 0.0
        self.zoom_factor = 1.0
        self.is_dragging = False