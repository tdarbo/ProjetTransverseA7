from settings import *


class SoundManager:
    def __init__(self, frequency=44100, size=-16, channels=2, buffer=512):
        pygame.mixer.init(frequency, size, channels, buffer)


    def play_music(self, music_path: str, loops: int = -1, fade_ms: int = 1000):
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.play(loops=loops, fade_ms=fade_ms)
            print(f"[SoundManager] Lecture musique: {music_path}")


    def play_sound(self, sound_path: str):

            sound = pygame.mixer.Sound(sound_path)
            sound.set_volume(VOLUME_SOUND)
            channel = pygame.mixer.find_channel()
            if channel:
                channel.play(sound)
                print(f"[SoundManager] Son joué: {sound_path}")
            else:
                print("[SoundManager] Aucun canal libre, le son ne peut pas être joué")

