from settings import *
from player import Player
from tile import Tile
from level import Level
from score import ScoreManager


def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.FULLSCREEN)
    pygame.display.set_caption("GOAT")
    clock = pygame.time.Clock()

    # Création des joueurs
    player1 = Player((255, 0, 0), (100, 100), BALL_RADIUS, BALL_MASS)
    player2 = Player((0, 0, 255), (200, 200), BALL_RADIUS, BALL_MASS)
    players = [player1, player2]

    # Initalisation du nombre de tours
    hole_number = 3 # Modifier après création des niveaux

    # Création des tiles
    tile_grass = Tile(
        tile_id="grass",
        x=0,
        y=0,
        width=WINDOW_WIDTH//3,
        height=WINDOW_HEIGHT,
        color="#6BC062"
    )

    tile_sand = Tile(
        tile_id="sand",
        x=WINDOW_WIDTH//3,
        y=0,
        width=WINDOW_WIDTH//3,
        height=WINDOW_HEIGHT,
        color="#Ffff00"
    )

    tile_ice = Tile(
        tile_id="ice",
        x=(WINDOW_WIDTH//3)*2,
        y=0,
        width=WINDOW_WIDTH //3,
        height=WINDOW_HEIGHT,
        color="#8cd3ff")

    tile_obstacle = Tile(
        tile_id="obstacle",
        x=WINDOW_WIDTH//2,
        y=WINDOW_HEIGHT//2,
        width=200,
        height=200,
        color="#5A3A3E"
    )
    map_tiles = [tile_grass, tile_sand, tile_ice, tile_obstacle]

    score_manager = ScoreManager(players,hole_number)
    # Création du niveau
    level = Level(map_tiles, players, score_manager)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                level.process_event(event)

        level.update(dt)
        screen.fill(pygame.Color("#BDDFFF"))
        level.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
