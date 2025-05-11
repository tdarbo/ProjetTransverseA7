from settings import *


class SoundManager:
    def __init__(self, frequency=44100, size=-16, channels=2, buffer=512):
        # Initialise le système audio de pygame
        pygame.mixer.init(frequency, size, channels, buffer)

    def play_music(self, music_path: str, loops: int = -1, fade_ms: int = 1000):
        # Charge un fichier à jouer en tant que musique
        pygame.mixer.music.load(music_path)
        # Joue la musique en boucle
        pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
        # Définit le volume de la musique
        pygame.mixer.music.set_volume(VOLUME_MUSIC)
        if DEBUG_MODE:
            print(f"[SoundManager] Lecture musique: {music_path}")

    def play_sound(self, sound_path: str):
        # On charge un son
        sound = pygame.mixer.Sound(sound_path)
        # Définit le volume du son
        sound.set_volume(VOLUME_SOUND)
        # On cherche un channel pour jouer le son
        channel = pygame.mixer.find_channel()
        if channel:
            # Joue le son sur ce channel
            channel.play(sound)
            if DEBUG_MODE:
                print(f"[SoundManager] Son joué: {sound_path}")
        else:
            # Aucun channel disponible pour jouer le son
            if DEBUG_MODE:
                print("[SoundManager] Aucun canal libre, le son ne peut pas être joué")

