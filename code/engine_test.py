from settings import *
from player import Player
from level import Level
from score import ScoreManager
from map import *


def main():
    pygame.init()
    w, h = pygame.display.list_modes()[0]
    screen = pygame.display.set_mode((w, h), pygame.FULLSCREEN)
    pygame.display.set_caption("GOAT")
    clock = pygame.time.Clock()

    # Création des joueurs
    player1 = Player((255, 0, 0), (100, 100), BALL_RADIUS, BALL_MASS)
    player2 = Player((0, 0, 255), (200, 200), BALL_RADIUS, BALL_MASS)
    players = [player1, player2]

    # Initialisation du nombre de tours
    hole_number = 3

    # Initialisation de la carte
    map01 = Map("../asset/TiledProject/maps/hole1.tmx", screen)

    # Initialisation du score
    score_manager = ScoreManager(players, hole_number)

    # Création du niveau
    level = Level(map01, players, score_manager, w, h)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                level.process_event(event)

        screen.fill(pygame.Color("#BDDFFF"))
        level.update(dt)
        level.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
