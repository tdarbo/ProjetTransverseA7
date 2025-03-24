from pygame import *

from camera_animator import *
from settings import *
from player import Player
from tile import Tile
from level import Level
from score import ScoreManager
from map import *

def main():
    pygame.init()
    w, h = pygame.display.list_modes()[0]
    screen = pygame.display.set_mode((w, h), pygame.NOFRAME)
    pygame.display.set_caption("GOAT")
    clock = pygame.time.Clock()

    # Création des joueurs
    player1 = Player((255, 0, 0), (100, 100), BALL_RADIUS, BALL_MASS)
    player2 = Player((0, 0, 255), (200, 200), BALL_RADIUS, BALL_MASS)
    players = [player1, player2]

    # Initalisation du nombre de tours
    hole_number = 3 # Modifier après création des niveaux

    map01 = Map("D:/DEV/WOKRSPACE/Pycharm/ProjetTransverseA7/asset/TiledProject/maps/hole1.tmx", screen)

    score_manager = ScoreManager(players,hole_number)
    # Création du niveau
    level = Level(map01, players, score_manager)

    map01.teleportPlayersToSpawn(players)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        #map.camera.update(pygame.event.get())



        for event in pygame.event.get():
            map01.camera.update(event)
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:  # Si une touche est pressée
                if event.key == pygame.K_SPACE:  # Si c'est la barre espace
                    level.centerOnCurrentPlayer()
            else:
                level.process_event(event)

        level.map.camera.animator.update()

        level.update(dt)
        screen.fill(pygame.Color("#BDDFFF"))
        level.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
