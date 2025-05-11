import pygame
import pygame.image
# Il faut toujours utiliser PIL pour la lecture initiale des GIFs, car pygame
# ne peut pas lire directement plusieurs frames d'un GIF
from PIL import Image

# Cache pour éviter de recharger les mêmes GIFs
GIF_CACHE = {}


def get_gif_frames(path: str, scale_factor: float = 1.0):
    """Charge les frames d'un GIF avec mise en cache et préscaling en utilisant seulement pygame"""

    cache_key = f"{path}_{scale_factor}"
    # On retourne les frames du cache si disponibles
    if cache_key in GIF_CACHE:
        return GIF_CACHE[cache_key]

    try:
        gif = Image.open(path)
        frame_data = []
        duration = []

        for frame in range(gif.n_frames):
            gif.seek(frame)
            frame = gif.convert("RGBA")

            # Convertir en surface pygame
            pygame_image = pygame.image.frombytes(frame.tobytes(), frame.size, "RGBA")

            # Redimensionner avec pygame
            if scale_factor != 1.0:
                pygame_image = pygame.transform.scale_by(pygame_image, scale_factor)

            frame_data.append(pygame_image)

            # On récupère la durée de la frame (en ms)
            duration.append(gif.info.get('duration', 100))

        # On stocke les frames avec leur durée
        frames = {'data': frame_data, 'duration': duration}

        # On termine par la mise en cache
        GIF_CACHE[cache_key] = frames
        return frames

    except Exception as e:
        print(f"Erreur lors du chargement du GIF {path}: {str(e)}")
        return {'data': [], 'duration': []}


class Gif:
    def __init__(self, gif_path: str, x: int, y: int, scale_factor: float, map_anchored: bool, hide: bool) -> None:
        self.gif_data = get_gif_frames(gif_path, scale_factor)
        self.frames = self.gif_data['data']
        self.durations = self.gif_data['duration']
        self.path = gif_path

        self.current_frame = 0
        self.max_frame = len(self.frames) if self.frames else 0

        self.x, self.y = x, y
        self.map_anchored = map_anchored
        self.hide = hide

        self.last_update = pygame.time.get_ticks()

        self.current_duration = self.durations[0] if self.max_frame > 0 else 100

    def update(self, surface: pygame.Surface):
        if self.hide or self.max_frame == 0:
            return

        # Afficher la frame actuelle
        surface.blit(self.frames[self.current_frame], (self.x, self.y))

        current_time = pygame.time.get_ticks()
        if current_time - self.last_update < self.current_duration:
            return

        self.last_update = current_time

        # Passer à la frame suivante
        self.current_frame = (self.current_frame + 1) % self.max_frame
        # Mettre à jour la durée pour la prochaine frame
        self.current_duration = self.durations[self.current_frame]

    def reset(self):
        """Réinitialise l'animation"""
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()

    def set_position(self, x: int, y: int):
        """Permet de repositionner le GIF"""
        self.x, self.y = x, y
