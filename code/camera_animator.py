from math import cos, pi


class CameraAnimator:
    def __init__(self, speed_factor=2.00):
        self.animations = []
        self.speed_factor = speed_factor  # Facteur de vitesse par défaut (2x plus rapide)

    def set_speed_factor(self, speed_factor):
        """Sets the global speed factor for all animations."""
        self.speed_factor = speed_factor

    def get_speed_factor(self):
        """Returns the current speed factor."""
        return self.speed_factor

    def update(self):
        """Met à jour toutes les animations actives."""
        for animation in self.animations[:]:
            # On passe le facteur de vitesse à chaque animation
            animation.update(self.speed_factor)
            if animation.is_finished():
                self.animations.remove(animation)

    def posToPos(self, camera, target_pos, duration):
        """Anime le déplacement de la caméra vers target_pos (coo carte)."""
        self.animations.append(CameraMoveAnimation(camera, target_pos, duration))

    def zoomToZoom(self, camera, target_zoom, duration):
        """Anime le zoom de la caméra vers target_zoom."""
        self.animations.append(CameraZoomAnimation(camera, target_zoom, duration))

    def posToPosAndZoom(self, camera, target_pos, target_zoom, duration):
        """Anime le déplacement et le zoom de la caméra."""
        self.animations.append(CameraMoveZoomAnimation(camera, target_pos, target_zoom, duration))


class CameraMoveAnimation:
    def __init__(self, camera, target_pos, duration):
        self.camera = camera
        self.start_x = camera.offset_X
        self.start_y = camera.offset_Y
        self.target_x = target_pos[0]
        self.target_y = target_pos[1]
        self.duration = duration
        self.elapsed_time = 0

    def update(self, speed_factor=1.0):
        # On augmente le temps écoulé selon le facteur de vitesse
        self.elapsed_time += speed_factor
        t = min(self.elapsed_time / self.duration, 1)
        # Formule pour avoir un mouvement fluide avec accélération/décélération
        t = 0.5 - 0.5 * cos(t * pi)
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

    def update(self, speed_factor=1.0):
        # On accélère l'animation selon le facteur de vitesse global
        self.elapsed_time += speed_factor
        t = min(self.elapsed_time / self.duration, 1)
        t = 0.5 - 0.5 * cos(t * pi)
        self.camera.zoom_factor = self.start_zoom + (self.target_zoom - self.start_zoom) * t

    def is_finished(self):
        return self.elapsed_time >= self.duration


class CameraMoveZoomAnimation:
    def __init__(self, camera, target_pos, target_zoom, duration):
        # On combine les deux animations pour un effet simultané
        self.move_anim = CameraMoveAnimation(camera, target_pos, duration)
        self.zoom_anim = CameraZoomAnimation(camera, target_zoom, duration)

    def update(self, speed_factor=1.0):
        # Application du même facteur aux deux animations
        self.move_anim.update(speed_factor)
        self.zoom_anim.update(speed_factor)

    def is_finished(self):
        return self.move_anim.is_finished() and self.zoom_anim.is_finished()