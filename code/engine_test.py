from settings import *
from player import Player
from tile import Tile

WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
VELOCITY_THRESHOLD = 1
FORCE_MULTIPLIER = 5
BALL_RADIUS = 15
TILE_SIZE = 32
BALL_MASS = 0.05

class Engine:
    """Gestion de la physique et des collisions"""
    def __init__(self, level):
        self.level = level

    def update(self, dt):
        for player in self.level.players:
            # position
            player.position += player.velocity * dt
            # friction
            friction = 0.98
            player.velocity *= friction

            self.resolve_player_wall_collision(player)
            player.update()

        # Collisions entre joueurs
        for i in range(len(self.level.players)):
            for j in range(i + 1, len(self.level.players)):
                self.resolve_player_player_collision(self.level.players[i], self.level.players[j])

        # Collisions avec obstacles
        for player in self.level.players:
            for tile in self.level.map_tiles:
                if tile.id == "obstacle" and player.rect.colliderect(tile.rect):
                    self.resolve_player_tile_collision(player, tile)

    def resolve_player_wall_collision(self, player):
        """collisions avec les bords de la fenêtre."""
        if player.position.x - player.radius < 0:
            player.position.x = player.radius
            player.velocity.x = -player.velocity.x
        if player.position.x + player.radius > WINDOW_WIDTH:
            player.position.x = WINDOW_WIDTH - player.radius
            player.velocity.x = -player.velocity.x
        if player.position.y - player.radius < 0:
            player.position.y = player.radius
            player.velocity.y = -player.velocity.y
        if player.position.y + player.radius > WINDOW_HEIGHT:
            player.position.y = WINDOW_HEIGHT - player.radius
            player.velocity.y = -player.velocity.y

    def resolve_player_player_collision(self, player1, player2):
        """collision entre deux joueurs."""
        pass

    def resolve_player_tile_collision(self, player, tile):
        """collision entre un joueur et une tile obstacle."""
        intersection = player.rect.clip(tile.rect)
        if intersection.width == 0 or intersection.height == 0:
            return

        if intersection.width < intersection.height:
            if player.rect.centerx < tile.rect.centerx:
                player.position.x -= intersection.width
            else:
                player.position.x += intersection.width
            player.velocity.x = -player.velocity.x
        else:
            if player.rect.centery < tile.rect.centery:
                player.position.y -= intersection.height
            else:
                player.position.y += intersection.height
            player.velocity.y = -player.velocity.y

        player.rect.center = (int(player.position.x), int(player.position.y))


class Level:
    """Gestion de la map, des tours et des événements"""

    def __init__(self, map_tiles, players):
        self.map_tiles = map_tiles
        self.players = players
        self.engine = Engine(self)
        self.current_player_index = 0
        self.current_player = players[0]
        self.shot_taken = False  # Indique si le joueur actif a déjà joué

        # Variables pour le drag & drop
        self.dragging = False
        self.drag_start = None # Vector
        self.drag_current = None # Vector
        self.force_multiplier = FORCE_MULTIPLIER

    def process_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            self.on_mouse_down(event)
        elif event.type == pygame.MOUSEMOTION:
            self.on_mouse_motion(event)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.on_mouse_up(event)

    def on_mouse_down(self, event):
        # Empêche le drag & drop si le coup a déjà été joué
        if self.shot_taken:
            return
        # Vérifie si le clic est sur la balle du joueur
        if self.current_player.rect.collidepoint(event.pos):
            self.dragging = True
            # Fixe le point de départ au centre de la balle
            self.drag_start = Vector(self.current_player.rect.center)
            self.drag_current = Vector(event.pos)

    def on_mouse_motion(self, event):
        if self.dragging:
            self.drag_current = Vector(event.pos)

    def on_mouse_up(self, event):
        if self.dragging:
            pos = Vector(event.pos)
            # Calcul de la force à appliquer : différence entre le centre de la balle et le point relâché
            force = (self.drag_start - pos) * self.force_multiplier
            self.current_player.velocity += force
            self.dragging = False
            self.shot_taken = True
            self.drag_start = None
            self.drag_current = None

    def update(self, dt):
        self.engine.update(dt)
        for player in self.players:
            player.update()
        self.check_turn_end()

    def check_turn_end(self):
        """Passe au joueur suivant si le joueur actif a joué et que sa vitesse est faible."""
        if self.shot_taken and self.current_player.velocity.length() < VELOCITY_THRESHOLD:
            self.next_turn()

    def next_turn(self):
        self.shot_taken = False
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        self.current_player = self.players[self.current_player_index]
        print(f"Tour du joueur {self.current_player_index + 1}")

    def draw(self, screen):
        for tile in self.map_tiles:
            tile.draw(screen)
        for player in self.players:
            player.draw(screen)
        # Indique le joueur qui doit joueur cercle blanc
        if not self.shot_taken:
            pygame.draw.circle(screen, pygame.Color("white"), self.current_player.rect.center, self.current_player.radius + 5, 2)
        # Affiche la ligne de visée
        if self.dragging and self.drag_start and self.drag_current:
            pygame.draw.line(screen, pygame.Color("black"), self.drag_start, self.drag_current, 3)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    pygame.display.set_caption("GOAT")
    clock = pygame.time.Clock()

    # Création des joueurs
    player1 = Player((255, 0, 0), (100, 100), BALL_RADIUS, BALL_MASS)
    player2 = Player((0, 0, 255), (200, 200), BALL_RADIUS, BALL_MASS)
    players = [player1, player2]

    # Création des tiles
    tile_background = Tile(
        tile_id="grass",
        x=TILE_SIZE,
        y=TILE_SIZE,
        width=WINDOW_WIDTH - (2 * TILE_SIZE),
        height=WINDOW_HEIGHT - (2 * TILE_SIZE),
        color="#6BC062"
    )
    tile_obstacle = Tile(
        tile_id="obstacle",
        x=WINDOW_WIDTH//2,
        y=WINDOW_HEIGHT//2,
        width=200,
        height=200,
        color="#5A3A3E"
    )
    map_tiles = [tile_background, tile_obstacle]

    # Création du niveau
    level = Level(map_tiles, players)

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
