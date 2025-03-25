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
        self.players = level.players


    def update_positions(self, dt):
        for player in self.players:
            # Formule pour modifier la position du joueur
            player.position += player.velocity * dt
            player.update()


    def apply_friction(self, dt):
        """Applique la friction à chaque joueur"""
        for player in self.players:
            friction = self.get_friction_at_point(player.position)
            # Formule exponentielle pour les frictions
            player.velocity *= exp(-(friction / BALL_MASS) * dt)


    def get_friction_at_point(self, point):
        """Donne le coefficient de friction du sol à une position."""
        for tile in self.level.map.tiles:
            if tile.rect.collidepoint(point):
                if tile.id == "Grass":
                    return GROUND_GRASS_FRICTION
                elif tile.id == "Sand":
                    return GROUND_SAND_FRICTION
                elif tile.id == "ice":
                    return GROUND_ICE_FRICTION
        # Par défaut = friction de l'herbe
        return GROUND_GRASS_FRICTION


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


    def update(self, dt):
        """Met à jour l'état du jeu en fonction du temps écoulé."""

        self.update_positions(dt)
        self.apply_friction(dt)

        # Gestion des collisions entre joueurs
        num_players = len(self.players)
        for i in range(num_players):
            for j in range(i + 1, num_players):
                self.resolve_player_player_collision(self.players[i], self.players[j])

        # Gestion des collisions avec les obstacles
        for player in self.level.players:
            for tile in self.level.map.tiles:
                if tile.id == "Collision" and player.rect.colliderect(tile.rect):
                    self.resolve_player_obstacle_collision(player, tile)

        self.resolve_out_of_bounds()
        self.resolve_finish()

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
        for tile in self.level.map.tiles:
            if tile.rect.collidepoint(player.position):
                return False
        return True

    def resolve_finish(self) -> None:
        for player in self.level.players:
            if self.is_on_finish(player):
                print(f"Player:{player.name} is on finish")


    def is_on_finish(self, player: Player) -> bool:
        """
        Vérifie si un joueur est sur un objet de la carte.
        @param player: Joueur vérifié
        @return: Si le joueur est sur l'objet de la carte
        """
        return False
        # if player.rect.collideobjects(self.level.map.hole):
        #     return True

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