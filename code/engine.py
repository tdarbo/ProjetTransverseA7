from pygame.examples.glcube import init_gl_stuff_old

from bonus_manager import BonusSpeed, BonusFantome, BonusAimant

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

        if isinstance(player1.bonus, BonusFantome) and player1.bonus.active:
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
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return
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
        Enhanced collision resolution that handles tile gaps and prevents oscillation.
        """
        import pygame
        from math import sqrt

        # Skip if ghost bonus is active
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return

        # Store original data for debug and comparison
        original_velocity = player.velocity.copy()
        original_position = player.position.copy()

        # Get the intersection rectangle between player and tile
        intersection = player.rect.clip(tile.rect)

        # Calculate penetration in X and Y directions
        pen_x = intersection.width
        pen_y = intersection.height

        # Skip if there's no actual penetration (prevents oscillation)
        if pen_x == 0 and pen_y == 0:
            return

        # Calculate distances to each edge of the tile
        dist_left = abs(player.rect.right - tile.rect.left)
        dist_right = abs(player.rect.left - tile.rect.right)
        dist_top = abs(player.rect.bottom - tile.rect.top)
        dist_bottom = abs(player.rect.top - tile.rect.bottom)

        # Find the minimum distance to determine the collision side
        min_dist = min(dist_left, dist_right, dist_top, dist_bottom)

        # Set default collision information
        normal = Vector(0, 0)
        collision_type = ""

        # Add a small buffer to prevent getting stuck in gaps
        buffer = 1.0

        # Resolve based on the minimum distance
        if min_dist == dist_left:
            # Colliding with left edge of tile
            player.position.x = tile.rect.left - player.radius - buffer
            player.velocity.x = -abs(player.velocity.x)  # Ensure velocity is away from tile
            normal = Vector(-1, 0)
            collision_type = "left edge"

        elif min_dist == dist_right:
            # Colliding with right edge of tile
            player.position.x = tile.rect.right + player.radius + buffer
            player.velocity.x = abs(player.velocity.x)  # Ensure velocity is away from tile
            normal = Vector(1, 0)
            collision_type = "right edge"

        elif min_dist == dist_top:
            # Colliding with top edge of tile
            player.position.y = tile.rect.top - player.radius - buffer
            player.velocity.y = -abs(player.velocity.y)  # Ensure velocity is away from tile
            normal = Vector(0, -1)
            collision_type = "top edge"

        elif min_dist == dist_bottom:
            # Colliding with bottom edge of tile
            player.position.y = tile.rect.bottom + player.radius + buffer
            player.velocity.y = abs(player.velocity.y)  # Ensure velocity is away from tile
            normal = Vector(0, 1)
            collision_type = "bottom edge"

        # Apply a minimum velocity to escape the collision
        min_escape_velocity = 20.0

        # Ensure the velocity is sufficient to escape the collision
        if normal.x != 0:
            if abs(player.velocity.x) < min_escape_velocity:
                player.velocity.x = normal.x * min_escape_velocity

        if normal.y != 0:
            if abs(player.velocity.y) < min_escape_velocity:
                player.velocity.y = normal.y * min_escape_velocity

        # Prevent excessive speed after collision
        max_collision_speed = MAX_PLAYER_VELOCITY.length()
        current_speed = player.velocity.length()

        if current_speed > max_collision_speed:
            player.velocity *= (max_collision_speed / current_speed)

        # IMPORTANT: Update the rect position after changing the player position
        player.rect.x = int(player.position.x)
        player.rect.y = int(player.position.y)

        # Add debug visualization if DEBUG_MODE is enabled
        if DEBUG_MODE:
            # Print collision information
            print(f"Collision: {player.name} hit {collision_type} - Pen X: {pen_x}, Pen Y: {pen_y}")
            print(
                f"  Original pos: ({original_position.x:.1f}, {original_position.y:.1f}) → New pos: ({player.position.x:.1f}, {player.position.y:.1f})")
            print(
                f"  Original vel: ({original_velocity.x:.1f}, {original_velocity.y:.1f}) → New vel: ({player.velocity.x:.1f}, {player.velocity.y:.1f})")

            # Ensure the debug_collisions list exists
            if not hasattr(self.level, 'debug_collisions'):
                self.level.debug_collisions = []

            # Store collision data for debug rendering
            self.level.debug_collisions.append({
                'position': original_position,
                'normal': normal,
                'velocity': player.velocity.copy(),
                'original_velocity': original_velocity,
                'time': pygame.time.get_ticks(),
            })

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

    def update(self, dt: float) -> None:
        """Met à jour la physique du jeu pour tous les joueurs avec un système de collision robuste."""

        for player in self.players:
            if player.finished:
                continue

            # 1. Update player physics
            self.update_position(player, dt)
            self.apply_friction(player, dt)

            # Apply aimant bonus if active
            if isinstance(player.bonus, BonusAimant) and player.bonus.isActive():
                self.apply_bonus_aimant(player)

            # Update player rect
            player.update()

            # 2. Check for bonus pickups
            self.resolve_bonus()

            # 3. Handle tile collisions with a more robust approach
            collision_detected = True
            max_iterations = 3  # Limit resolution attempts to prevent infinite loops
            iterations = 0

            while collision_detected and iterations < max_iterations:
                iterations += 1
                collision_detected = False

                # First handle obstacle collisions
                for tile in self.level.map.tiles:
                    if tile.id == "Collision" and player.rect.colliderect(tile.rect):
                        self.resolve_player_obstacle_collision(player, tile)
                        collision_detected = True
                        # Update player rect after each resolution
                        player.update()

                # Then handle bounce tiles
                for tile in self.level.map.tiles:
                    if tile.id == "Bounce" and player.rect.colliderect(tile.rect):
                        self.resolve_player_bounce_collision(player, tile)
                        collision_detected = True
                        # Update player rect after each resolution
                        player.update()

            # If we hit max iterations, the player might be stuck - apply a small random impulse
            if iterations == max_iterations and collision_detected:
                # Apply a small random impulse to help escape
                import random
                player.velocity.x += random.uniform(-50, 50)
                player.velocity.y += random.uniform(-50, 50)
                player.update()

            # 4. Check for out of bounds and finish conditions
            self.resolve_out_of_bounds(player)
            self.is_on_finish(player)

        # 5. Handle player-player collisions after all individual physics
        for i in range(len(self.players)):
            for j in range(i + 1, len(self.players)):
                self.resolve_player_player_collision(self.players[i], self.players[j])

        # 6. Final update for all players
        for player in self.players:
            player.update()

    def apply_bonus_aimant(self, player:Player):
        """
        Applique le bonus d'aimant à un joueur.
        """
        hole_x, hole_y = self.level.map.hole.x, self.level.map.hole.y
        hole = pygame.math.Vector2(hole_x, hole_y)
        pos = player.position  # Supposé être un Vector2 aussi
        direction = hole - pos
        attraction_force = direction.normalize() * (1 / max(direction.length(), 0.001)*5) * 100
        player.velocity += attraction_force
