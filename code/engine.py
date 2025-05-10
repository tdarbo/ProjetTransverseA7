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
        Gère la collision entre un joueur et une tuile obstacle avec une détection
        améliorée pour éviter les multi-collisions et détecter les coins manqués.
        """
        import math

        # Skip collision for ghost bonus
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return

        SPEED_REDISTRIBUTION = 0.5

        # Prevent multiple collisions in a single frame
        current_time = pygame.time.get_ticks()
        if hasattr(player, 'last_collision_time') and current_time - player.last_collision_time < 50:  # 50ms cooldown
            return
        player.last_collision_time = current_time

        # Store original velocity for validation later
        original_velocity = player.velocity.copy() * SPEED_REDISTRIBUTION
        original_direction = original_velocity.normalize() if original_velocity.length() > 0 else Vector(0, 0)

        # Basic collision detection
        intersection = player.rect.clip(tile.rect)
        pen_x = intersection.width
        pen_y = intersection.height

        # Check for narrow intersections that might indicate a corner or gap
        narrow_threshold = player.radius // 3
        is_narrow_hit = (pen_x < narrow_threshold or pen_y < narrow_threshold)

        # Enhanced collision detection for narrow hits
        if is_narrow_hit:
            # Setup collision points to check (multiples around the ball's perimeter)
            check_points = []
            # Add points in the velocity direction and perpendicular to velocity
            if original_velocity.length() > 0:
                # Direction of travel - more points
                dir_norm = original_velocity.normalize()
                check_points.append((player.position.x + dir_norm.x * player.radius,
                                     player.position.y + dir_norm.y * player.radius))

                # Points to the sides of direction
                perp_dir = Vector(-dir_norm.y, dir_norm.x)  # Perpendicular vector
                check_points.append((player.position.x + perp_dir.x * player.radius * 0.7,
                                     player.position.y + perp_dir.y * player.radius * 0.7))
                check_points.append((player.position.x - perp_dir.x * player.radius * 0.7,
                                     player.position.y - perp_dir.y * player.radius * 0.7))
            else:
                # If not moving, check cardinal directions
                check_points.append((player.position.x + player.radius, player.position.y))
                check_points.append((player.position.x - player.radius, player.position.y))
                check_points.append((player.position.x, player.position.y + player.radius))
                check_points.append((player.position.x, player.position.y - player.radius))

            # Check if any of these points collide with neighboring tiles to handle gaps
            normals = []
            for x, y in check_points:
                point_rect = pygame.Rect(x - 1, y - 1, 2, 2)  # Small rect for point
                for neighbor_tile in self.level.map.tiles:
                    if neighbor_tile.id == "Collision" and point_rect.colliderect(neighbor_tile.rect):
                        # Calculate normal for this point
                        point_normal = Vector(0, 0)

                        # Determine which side was hit
                        if x < neighbor_tile.rect.left:
                            point_normal.x = -1
                        elif x > neighbor_tile.rect.right:
                            point_normal.x = 1

                        if y < neighbor_tile.rect.top:
                            point_normal.y = -1
                        elif y > neighbor_tile.rect.bottom:
                            point_normal.y = 1

                        # Normalize this normal and add to list if valid
                        if point_normal.length() > 0:
                            point_normal = point_normal.normalize()
                            normals.append(point_normal)

            # If we found multiple normals, average them
            if len(normals) > 0:
                normal = Vector(0, 0)
                for n in normals:
                    normal += n
                if normal.length() > 0:
                    normal = normal.normalize()
                else:
                    # Default to standard collision if normals cancel out
                    normal = self._calculate_standard_normal(player, tile, pen_x, pen_y)
            else:
                # Fall back to standard collision
                normal = self._calculate_standard_normal(player, tile, pen_x, pen_y)
        else:
            # Standard collision for clear hits
            normal = self._calculate_standard_normal(player, tile, pen_x, pen_y)

        # Apply standard collision response with the normal
        self._apply_collision_response(player, tile, normal, original_velocity, original_direction, pen_x, pen_y)

        # Mark this collision for visualization in the debug renderer
        if DEBUG_MODE:
            self.level.debug_collisions.append({
                'position': player.position.copy(),
                'normal': normal.copy(),
                'velocity': player.velocity.copy(),
                'time': current_time,
            })

    def _calculate_standard_normal(self, player, tile, pen_x, pen_y):
        """Calculate standard collision normal based on intersection dimensions."""
        normal = Vector(0, 0)

        # Check for corner collision first
        corner_threshold = 5  # Pixels difference to consider it a corner hit
        is_corner_hit = abs(pen_x - pen_y) < corner_threshold

        if is_corner_hit:
            # Handle corner collision
            if player.rect.centerx < tile.rect.centerx:
                normal.x = -1
            else:
                normal.x = 1

            if player.rect.centery < tile.rect.centery:
                normal.y = -1
            else:
                normal.y = 1

            if DEBUG_MODE:
                print(f"Corner collision detected for {player.name}")
        else:
            # Regular edge collision
            if pen_x < pen_y:
                # Collision from left or right
                if player.rect.centerx < tile.rect.centerx:
                    player.position.x -= pen_x
                    normal = Vector(-1, 0)
                    if DEBUG_MODE:
                        print(f"Left edge collision for {player.name}")
                else:
                    player.position.x += pen_x
                    normal = Vector(1, 0)
                    if DEBUG_MODE:
                        print(f"Right edge collision for {player.name}")
            else:
                # Collision from top or bottom
                if player.rect.centery < tile.rect.centery:
                    player.position.y -= pen_y
                    normal = Vector(0, -1)
                    if DEBUG_MODE:
                        print(f"Top edge collision for {player.name}")
                else:
                    player.position.y += pen_y
                    normal = Vector(0, 1)
                    if DEBUG_MODE:
                        print(f"Bottom edge collision for {player.name}")

        return normal.normalize() if normal.length() > 0 else Vector(1, 0)

    def _apply_collision_response(self, player, tile, normal, original_velocity, original_direction, pen_x, pen_y):
        """Apply physical collision response without randomness."""
        import math

        # Reposition the player along the normal (outside the collision)
        reposition_amount = max(pen_x, pen_y) * 1.1  # Slightly more to ensure it's outside
        player.position += normal * reposition_amount

        # Apply proper reflection physics
        # Formula: v_reflected = v - 2 * (v·n) * n
        dot_product = player.velocity.dot(normal)
        player.velocity -= normal * 2 * dot_product

        # Validate the reflected velocity - check if it's too similar to incoming direction
        new_direction = player.velocity.normalize() if player.velocity.length() > 0 else Vector(0, 0)
        similarity = original_direction.dot(new_direction)

        if DEBUG_MODE:
            print(f"Similarity: {similarity:.4f}, Original: {original_direction}, New: {new_direction}")

        # Handle improper bounces (likely due to precision/floating point issues)
        is_improper_bounce = similarity > 0.85  # >0.85 means less than about 30° difference
        if is_improper_bounce:
            if DEBUG_MODE:
                print(f"Detected improper bounce for {player.name}! Applying fallback correction.")

            # Force a 45-degree reflection based on the normal
            # Calculate perpendicular vector to normal
            perp_normal = Vector(-normal.y, normal.x)

            # Create a deflection vector (45 degrees from normal)
            deflection = (normal + perp_normal).normalize()
            # Use original speed for consistency
            original_speed = original_velocity.length()
            player.velocity = deflection * original_speed

        # Final safety check - never allow a ball to bounce directly back
        final_direction = player.velocity.normalize()
        final_similarity = original_direction.dot(final_direction)

        if final_similarity < -0.95:  # Almost exactly opposite (back-bounce)
            if DEBUG_MODE:
                print(f"Preventing direct back-bounce for {player.name}")

            # Calculate a deflection angle (45 degrees from the normal)
            perp_normal = Vector(-normal.y, normal.x)
            deflection = (normal + perp_normal).normalize()

            # Apply the deflection while maintaining speed
            original_speed = original_velocity.length()
            player.velocity = deflection * original_speed

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
        """Met à jour la physique du jeu pour tous les joueurs."""

        for i in range(self.num_players):
            player = self.players[i]

            # Mise à jour de la position du joueur
            self.update_position(player, dt)

            player.update()

            if isinstance(player.bonus, BonusAimant) and player.bonus.isActive():
                self.apply_bonus_aimant(player)

            # Application de la friction
            self.apply_friction(player, dt)

            # Gestion des collisions entre joueurs
            for j in range(i + 1, self.num_players):
                self.resolve_player_player_collision(player, self.players[j])

            player.update()

            # Gestion des collisions avec la map
            for tile in self.level.map.tiles:
                if tile.id == "Collision" and player.rect.colliderect(tile.rect):
                    self.resolve_player_obstacle_collision(player, tile)

            for tile in self.level.map.tiles:
                if tile.id == "Bounce" and player.rect.colliderect(tile.rect):
                    self.resolve_player_bounce_collision(player, tile)

            player.update()

            self.resolve_out_of_bounds(player)
            self.is_on_finish(player)
            self.resolve_bonus()

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
