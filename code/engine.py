from player import Player
from settings import *
from math import exp


class Engine:
    """Gestion de la physique et des collisions"""

    def __init__(self, level):
        """
        Initialise le moteur de physique.

        :param level: Le niveau de jeu contenant les joueurs et la carte.
        """
        self.level = level

    def update(self, dt):
        """
        Met à jour l'état du jeu en fonction du temps écoulé.

        :param dt: Le temps écoulé depuis la dernière mise à jour.
        """
        for player in self.level.players:
            # Met à jour la position du joueur en fonction de sa vitesse
            player.position += player.velocity * dt

            # Détection du type de sol sous le joueur
            friction = GROUND_GRASS_FRICTION  # Par défaut, herbe
            for tile in self.level.map_tiles:
                if tile.rect.collidepoint(player.position.x, player.position.y):
                    if tile.id == "Grass":
                        friction = GROUND_GRASS_FRICTION
                    elif tile.id == "Sand":
                        friction = GROUND_SAND_FRICTION
                    elif tile.id == "ice":
                        friction = GROUND_ICE_FRICTION
                    break  # On sort dès qu'on a trouvé la bonne tuile

            # Application de la friction
            player.velocity = player.velocity * exp(-(friction / BALL_MASS) * dt)

            # Gestion des collisions avec les murs
            #self.resolve_player_wall_collision(player)
            self.resolve_out_of_bounds()
            player.update()

        # Gestion des collisions entre joueurs
        for i in range(len(self.level.players)):
            for j in range(i + 1, len(self.level.players)):
                self.resolve_player_player_collision(self.level.players[i], self.level.players[j])

        # Gestion des collisions avec les obstacles
        for player in self.level.players:
            for tile in self.level.map_tiles:
                if tile.id == "Collision" and player.rect.colliderect(tile.rect):
                    self.resolve_player_obstacle_collision(player, tile)

    def resolve_out_of_bounds(self) -> None:
        """
        Gère les joueurs en dehors des limites de la carte.
        """
        for player in self.level.players:
            if self.is_out_of_bounds(player):
                self.level.map.teleportPlayerToSpawn(player)
                player.velocity = Vector(0, 0)
                print(f"Player:{player.name} is out of bounds")

    def is_out_of_bounds(self, player: Player) -> bool:
        """
        Vérifie si un joueur est en dehors des limites de la carte.
        @param player: Joueur vérifié
        @return: Si le joueur est en dehors des limites de la carte
        """
        for tile in self.level.map_tiles:
            if player.rect.colliderect(tile.rect):
                return False
        return True

    def resolve_finish(self) -> None:
        for player in self.level.players:
            if self.is_on_finish(player):
                print(f"Player:{player.name} is on finish")
        pass

    def is_on_finish(self, player: Player) -> bool:
        """
        Vérifie si un joueur est sur un objet de la carte.
        @param player: Joueur vérifié
        @return: Si le joueur est sur l'objet de la carte
        """
        if player.rect.collideobjects(self.level.map.hole):
            return True

    def resolve_player_wall_collision(self, player):
        """
        Gère les collisions entre un joueur et les bords de la fenêtre.

        :param player: Le joueur à vérifier pour les collisions avec les murs.
        """
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
        """
        Gère les collisions entre deux joueurs.

        :param player1: Le premier joueur impliqué dans la collision.
        :param player2: Le second joueur impliqué dans la collision.
        """
        diff = player1.position - player2.position
        distance = diff.length()
        min_distance = player1.radius + player2.radius

        if distance < min_distance:
            if distance != 0:
                normal = diff.normalize()
            else:
                normal = Vector(1, 0)

            # Évite que les joueurs ne fusionnent
            anti_superposition = min_distance - distance
            player1.position += normal * (anti_superposition / 2)
            player2.position -= normal * (anti_superposition / 2)

            v1 = player1.velocity.dot(normal)
            v2 = player2.velocity.dot(normal)

            # Formule de collision élastique
            player1.velocity += normal * (v2 - v1)
            player2.velocity += normal * (v1 - v2)

    def resolve_player_obstacle_collision(self, player, tile):
        """
        Gère les collisions entre un joueur et une tuile.

        :param player: Le joueur impliqué dans la collision.
        :param tile: La tuile impliquée dans la collision.
        """
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
