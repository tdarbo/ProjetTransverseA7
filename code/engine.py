from pygame.examples.glcube import init_gl_stuff_old

from bonus_manager import BonusSpeed
from player import Player
from settings import *
from math import exp,sqrt


class Engine:
    """Gère la physique, les collisions, et les interactions entre les joueurs et le terrain."""

    def __init__(self, level):
        """Initialise le moteur de jeu."""
        self.level = level
        self.players = level.players
        self.num_players = len(self.players)

    def inversionX(self, player : Player) -> int:
        if player.velocity.x > 0:
            return -1
        else :
            return 1

    def inversionY(self, player : Player) -> int:
        if player.velocity.y > 0:
            return -1
        else :
            return 1


    def update_position(self, player: Player, dt: float) -> None:
        """Met à jour la position du joueur en fonction de sa vitesse."""
        bonus_modifier = 1
        if isinstance(player.bonus, BonusSpeed):
            bonus_modifier = 2

        player.position += player.velocity * dt * bonus_modifier

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
                elif tile.id == "Ice":
                    return GROUND_ICE_FRICTION

        # Par défaut : herbe
        return GROUND_GRASS_FRICTION

    def resolve_player_player_collision(self, player1: Player, player2: Player) -> None:
        """Résout une collision entre deux joueurs."""
        if player1.finished or player2.finished:
            return

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
        for tile in self.level.map.tiles:
            if tile.rect.collidepoint(player.position) and tile.id != "Water":
                return False  # Le joueur est sur une tuile
        return True  # Le joueur n’est sur aucune tuile, il est "out of bounds"

    def resolve_finish(self, player: Player) -> None:
        """Vérifie si un joueur a terminé le niveau."""
        if not player.finished:
            print(f"Player:{player.name} has finished in x shots")
            player.velocity = Vector(0.0, 0.0)
            player.finished = True


    def is_on_finish(self, player: Player) -> None:
        """Vérifie si un joueur a atteint le trou."""
        hole = self.level.map.hole

        diff_x,diff_y = player.position.x - hole.x, player.position.y - hole.y

        distance = sqrt(diff_x ** 2 + diff_y ** 2)
        if distance < (BALL_RADIUS + 1):
            self.resolve_finish(player)

    # À implémenter si nécessaire :
    # return player.rect.collideobjects(self.level.map.hole)

    def resolve_player_obstacle_collision(self, player: Player, tile) -> None:
        """
        Gère la collision entre un joueur et une tuile obstacle.
        """
        intersection = player.rect.clip(tile.rect)

        # On calcule les superpositions sur X et Y
        pen_x = intersection.width
        pen_y = intersection.height

        # Résolution de la collision en X
        if pen_x < pen_y:
            if player.rect.centerx < tile.rect.centerx:
                # Le joueur est à gauche de la tile, on le décale vers la gauche
                player.position.x -= pen_x
            else:
                # Le joueur est à droite de la tile, on le décale vers la droite
                player.position.x += pen_x
            # On inverse la vélocité en X
            player.velocity.x = -player.velocity.x

        # Résolution de la collision en Y
        else:
            if player.rect.centery < tile.rect.centery:
                # Le joueur est au-dessus de la tile, on le décale vers le haut
                player.position.y -= pen_y
            else:
                # Le joueur est en dessous de la tile, on le décale vers le bas
                player.position.y += pen_y

            # On Inverse la vélocité en Y
            player.velocity.y = -player.velocity.y

    def resolve_bonus(self):
        for player in self.players:
            for bonus in self.level.map.bonuses:
                diff_x, diff_y = player.position.x - bonus.x, player.position.y - bonus.y

                distance = sqrt(diff_x ** 2 + diff_y ** 2)
                if distance < (BALL_RADIUS + 5) and bonus.available:
                    bonus.pick_bonus(player,self.players)

    def resolve_player_bounce_collision(self, player: Player, tile) -> None:
        """
        Gère la collision entre un joueur et une tuile bumper.
        """
        intersection = player.rect.clip(tile.rect)

        # On calcule les superpositions sur X et Y
        pen_x = intersection.width
        pen_y = intersection.height

        # Résolution de la collision en X
        if pen_x < pen_y:
            if player.rect.centerx < tile.rect.centerx:
                # Le joueur est à gauche de la tile, on le décale vers la gauche
                player.position.x -= pen_x
            else:
                # Le joueur est à droite de la tile, on le décale vers la droite
                player.position.x += pen_x
            # On inverse la vélocité en X
            player.velocity.x = self.inversionX(player) * MAX_PLAYER_VELOCITY.length()

        # Résolution de la collision en Y
        else:
            if player.rect.centery < tile.rect.centery:
                # Le joueur est au-dessus de la tile, on le décale vers le haut
                player.position.y -= pen_y
            else:
                # Le joueur est en dessous de la tile, on le décale vers le bas
                player.position.y += pen_y

            # On Inverse la vélocité en Y
            player.velocity.y = self.inversionY(player) * MAX_PLAYER_VELOCITY.length()

    def resolve_player_speed_right(self, player: Player) -> None:
        """
        Accelere le joueur vers la droite
        """
        if player.velocity.x > 0:
            player.velocity.x = player.velocity.x + player.velocity.x * 0.1
        else :
            player.velocity.x = player.velocity.x + player.velocity.x * 0.1 * (-1) + 1

    def resolve_player_speed_left(self, player: Player) -> None:
        """
        Accelere le joueur vers la gauche
        """
        if player.velocity.x > 0:
            player.velocity.x = player.velocity.x + player.velocity.x * 0.1 * (-1) - 10
        else :
            player.velocity.x = player.velocity.x + player.velocity.x * 0.1

    def resolve_player_speed_down(self, player: Player) -> None:
        """
        Accelere le joueur vers le bas
        """
        if player.velocity.y > 0:
            player.velocity.y = player.velocity.y + player.velocity.y * 0.1
        else :
            player.velocity.y = player.velocity.y + player.velocity.y * 0.1 * (-1) + 10

    def resolve_player_speed_up(self, player: Player) -> None:
        """
        Accelere le joueur vers le haut
        """
        if player.velocity.y > 0:
            player.velocity.y = player.velocity.y + player.velocity.y * 0.1 * (-1) - 10
        else :
            player.velocity.y = player.velocity.y + player.velocity.y * 0.1

    def update(self, dt: float) -> None:
        """Met à jour la physique du jeu pour tous les joueurs."""

        for i in range(self.num_players):
            player = self.players[i]

            #limitation de vitesse
            if player.velocity.y > 1000:
                player.velocity.y = 1000
            if player.velocity.y < -1000:
                player.velocity.y = -1000
            if player.velocity.x > 1000:
                player.velocity.x = 1000
            if player.velocity.x < -1000:
                player.velocity.x = -1000

            # Mise à jour de la position du joueur
            self.update_position(player, dt)

            player.update()

            # Application de la friction
            self.apply_friction(player, dt)

            # Gestion des collisions entre joueurs
            for j in range(i + 1, self.num_players):
                self.resolve_player_player_collision(player, self.players[j])

            player.update()

            # Gestion des collisions/bounce/accélerateur avec la map
            for tile in self.level.map.tiles:
                if tile.id == "Collision" and player.rect.colliderect(tile.rect):
                    self.resolve_player_obstacle_collision(player, tile)

                elif tile.id == "Bounce" and player.rect.colliderect(tile.rect):
                    self.resolve_player_bounce_collision(player, tile)

                elif tile.id == "Speed_right" and player.rect.colliderect(tile.rect):
                    self.resolve_player_speed_right(player)

                elif tile.id == "Speed_left" and player.rect.colliderect(tile.rect):
                    self.resolve_player_speed_left(player)

                elif tile.id == "Speed_down" and player.rect.colliderect(tile.rect):
                    self.resolve_player_speed_down(player)

                elif tile.id == "Speed_up" and player.rect.colliderect(tile.rect):
                    self.resolve_player_speed_up(player)
            player.update()

            self.resolve_out_of_bounds(player)
            self.is_on_finish(player)
            self.resolve_bonus()

            player.update()
