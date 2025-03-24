import pygame
import math

class CameraAnimator:
    def __init__(self):
        self.animations = []

    def update(self):
        """
        Met à jour toutes les animations actives.
        """
        for animation in self.animations[:]:  # Copie de la liste pour éviter les erreurs de suppression
            animation.update()
            if animation.is_finished():
                self.animations.remove(animation)

    def posToPos(self, camera, target_pos, duration):
        """
        Anime la caméra d'une position actuelle à une position cible.
        """
        self.animations.append(CameraMoveAnimation(camera, target_pos, duration))

    def posToPosAndZoom(self, camera, target_pos, target_zoom, duration):
        """
        Anime la caméra d'une position actuelle vers une position cible avec un zoom.
        """
        self.animations.append(CameraMoveZoomAnimation(camera, target_pos, target_zoom, duration))

    def zoomToZoom(self, camera, target_zoom, duration):
        """
        Anime uniquement le zoom de la caméra.
        """
        self.animations.append(CameraZoomAnimation(camera, target_zoom, duration))


class CameraMoveAnimation:
    def __init__(self, camera, target_pos, duration):
        self.camera = camera
        self.start_x = camera.offset_X
        self.start_y = camera.offset_Y

        # Calcul du décalage cible à partir de la position du monde
        screen_center_x = camera.screen.get_width() / 2
        screen_center_y = camera.screen.get_height() / 2

        self.target_x = target_pos[0] - screen_center_x
        self.target_y = target_pos[1] - screen_center_y

        self.duration = duration
        self.elapsed_time = 0

    def update(self):
        self.elapsed_time += 1
        t = min(self.elapsed_time / self.duration, 1)

        # Interpolation lissée (accélération/décélération)
        t = 0.5 - 0.5 * math.cos(t * math.pi)

        # Mise à jour de la position de la caméra
        self.camera.offset_X = self.start_x + (self.target_x - self.start_x) * t
        self.camera.offset_Y = self.start_y + (self.target_y - self.start_y) * t

    def is_finished(self):
        return self.elapsed_time >= self.duration

class CameraZoomAnimation:
    def __init__(self, camera, target_zoom, duration):
        self.camera = camera
        self.start_zoom = camera.zoom_factor
        self.target_zoom = target_zoom
        self.duration = duration
        self.elapsed_time = 0

    def update(self):
        self.elapsed_time += 1
        t = min(self.elapsed_time / self.duration, 1)

        # Interpolation lissée
        t = 0.5 - 0.5 * math.cos(t * math.pi)

        self.camera.zoom_factor = self.start_zoom + (self.target_zoom - self.start_zoom) * t

    def is_finished(self):
        return self.elapsed_time >= self.duration


class CameraMoveZoomAnimation:
    def __init__(self, camera, target_pos, target_zoom, duration):
        self.move_anim = CameraMoveAnimation(camera, target_pos, duration)
        self.zoom_anim = CameraZoomAnimation(camera, target_zoom, duration)

    def update(self):
        self.move_anim.update()
        self.zoom_anim.update()

    def is_finished(self):
        return self.move_anim.is_finished() and self.zoom_anim.is_finished()
