import pygame
import pygame.image
# Il faut utiliser PIL pour la lecture des GIFs, car pygame
# ne peut pas lire directement plusieurs frames d'un GIF
from PIL import Image

# Dictionnaire de cache pour ne pas recharger les mêmes GIFs plusieurs fois
GIF_CACHE = {}

def get_gif_frames(path: str, scale_factor: float = 1.0):
    """Charge les frames d'un GIF avec mise en cache et préscaling en utilisant seulement pygame"""

    cache_key = f"{path}_{scale_factor}"
    # Si le GIF est déjà chargé, on le réutilise
    if cache_key in GIF_CACHE:
        return GIF_CACHE[cache_key]

    try:
        gif = Image.open(path)  # On ouvre le fichier GIF avec Pillow
        frame_data = []  # Liste des frames (surface pygame)
        duration = []  # Liste des durées pour chaque frame (en ms)

        for frame in range(gif.n_frames):
            gif.seek(frame)  # On se "positionne" sur la frame n
            frame = gif.convert("RGBA")

            # Conversion de l'image PIL en Surface Pygame
            pygame_image = pygame.image.frombytes(frame.tobytes(), frame.size, "RGBA")

            # On redimensionne la frame si nécessaire
            if scale_factor != 1.0:
                pygame_image = pygame.transform.scale_by(pygame_image, scale_factor)

            frame_data.append(pygame_image)
            duration.append(gif.info.get('duration', 100))  # 100 ms par défaut

        frames = {'data': frame_data, 'duration': duration}
        GIF_CACHE[cache_key] = frames  # Mise en cache de la frame
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
