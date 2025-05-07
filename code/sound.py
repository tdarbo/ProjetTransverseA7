from settings import *


class SoundManager:
    def __init__(self, file_path):
        """ Le file_path doit être en .wav !!!"""
        self.sound = pygame.mixer.Sound(file_path)
        self.repeat = False
        self.nbr_loop = 0

    def play(self):
        """ Lance la musique un nombre de fois loop."""
        self.sound.play(self.nbr_loop)

    def pause(self):
        """ arrête la musique."""
        self.sound.stop()

    def set_volume(self, volume):
        """ Prend un paramètre un volume compris entre 0 et 1 qui détermine le pourcentage du volume de la musique qu'on
        va utiliser"""
        self.sound.set_volume(volume)

    def loop(self, repeat = False, nbr_loop = -1):
        """ Détermine si on doit jouer la musique à l'infini et sinon le nombre de fois où la musique se répètera. """
        self.repeat = repeat
        if not self.repeat:
            self.nbr_loop = -1
        else :
            self.nbr_loop = nbr_loop - 1

if __name__ == '__main__':
    pygame.mixer.init()
    s = SoundManager("../asset/musics/Lancement jeu.wav")
    s.play()