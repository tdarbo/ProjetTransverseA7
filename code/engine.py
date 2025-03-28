from player import Player
from settings import *
from math import exp

class Engine:
    """Gère la physique, les collisions, et les interactions entre les joueurs et le terrain."""

    def __init__(self, level):
        """Initialise le moteur de jeu."""
        self.level = level
        self.players = level.players
        self.num_players = len(self.players)

    def update_position(self, player: Player, dt: float) -> None:
        """Met à jour la position du joueur en fonction de sa vitesse."""
        player.position += player.velocity * dt

    def apply_friction(self, player: Player, dt: float) -> None:
        """Applique la friction du sol à un joueur."""
        friction = self.get_friction_at_point(player.position)
        # Formule exponentielle : simule une décroissance naturelle de la vitesse due à la friction
        player.velocity *= exp(-(friction / BALL_MASS) * dt)

    def get_friction_at_point(self, point: tuple[float, float]) -> float:
        """Retourne le coefficient de friction du terrain à une position donnée."""
        for tile in self.level.map.tiles:
            if tile.rect.collidepoint(point):
                if tile.id == "Grass":
                    return GROUND_GRASS_FRICTION
                elif tile.id == "Sand":
                    return GROUND_SAND_FRICTION
                elif tile.id == "ice":
                    return GROUND_ICE_FRICTION
        # Par défaut : herbe
        return GROUND_GRASS_FRICTION

    def resolve_player_player_collision(self, player1: Player, player2: Player) -> None:
        """Résout une collision entre deux joueurs."""
        diff = player1.position - player2.position
        distance = diff.length()
        min_distance = player1.radius + player2.radius

        if distance < min_distance:
            # Si les joueurs se superposent :
            normal = diff.normalize() if distance != 0 else Vector(1.0, 0.0)

            # Correction de la superposition (séparation équitable)
            overlap = min_distance - distance
            player1.position += normal * (overlap / 2)
            player2.position -= normal * (overlap / 2)

            # Projection des vitesses sur l’axe de collision
            v1 = player1.velocity.dot(normal)
            v2 = player2.velocity.dot(normal)

            # Échange des vitesses projetées (collision élastique sans perte d’énergie)
            player1.velocity += normal * (v2 - v1)
            player2.velocity += normal * (v1 - v2)

    def resolve_out_of_bounds(self, player: Player) -> None:
        """Gère le cas où un joueur sort des limites de la carte."""
        if self.is_out_of_bounds(player):
            player.velocity = Vector(0.0, 0.0)
            self.level.map.teleportPlayerToSpawn(player)
            print(f"Player:{player.name} is out of bounds")

    def is_out_of_bounds(self, player: Player) -> bool:
        """Vérifie si un joueur est en dehors du terrain."""
        for tile in self.level.map.tiles:
            if tile.rect.collidepoint(player.position):
                return False
        return True

    def resolve_finish(self, player: Player) -> None:
        """Vérifie si un joueur a terminé le niveau."""
        if self.is_on_finish(player):
            # Gérer le reste
            print(f"Player:{player.name} is on finish")

    def is_on_finish(self, player: Player) -> bool:
        """Vérifie si un joueur a atteint le trou."""
        return False
        # À implémenter si nécessaire :
        # return player.rect.collideobjects(self.level.map.hole)

    def resolve_player_obstacle_collision(self, player: Player, tile) -> None:
        """Gère la collision entre un joueur et une tuile obstacle."""
        intersection = player.rect.clip(tile.rect)

        if intersection.width == 0 or intersection.height == 0:
            return  # Pas de collision réelle

        if intersection.width < intersection.height:
            # Collision horizontale
            if player.rect.centerx < tile.rect.centerx:
                player.position.x -= intersection.width
            else:
                player.position.x += intersection.width
            player.velocity.x = -player.velocity.x
        else:
            # Collision verticale
            if player.rect.centery < tile.rect.centery:
                player.position.y -= intersection.height
            else:
                player.position.y += intersection.height
            player.velocity.y = -player.velocity.y

    def update(self, dt: float) -> None:
        """Met à jour la physique du jeu pour tous les joueurs."""
        for i in range(self.num_players):
            player = self.players[i]

            # Mise à jour de la position du joueur
            self.update_position(player, dt)

            # Application de la friction
            self.apply_friction(player, dt)

            player.update()

            # Gestion des collisions entre joueurs
            for j in range(i + 1, self.num_players):
                self.resolve_player_player_collision(player, self.players[j])

            # Gestion des collisions avec la map
            for tile in self.level.map.tiles:
                if tile.id == "Collision" and player.rect.colliderect(tile.rect):
                    self.resolve_player_obstacle_collision(player, tile)

            self.resolve_out_of_bounds(player)
            self.resolve_finish(player)

            player.update()
