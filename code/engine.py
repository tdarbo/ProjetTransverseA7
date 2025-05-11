import math
import random

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

    def resolve_shot(self, player: Player, velocity_vector: Vector):

        # if self.current_player.speed_bonus:
        #    new_velocity *= 2
        #    new_velocity = min(new_velocity, MAX_PLAYER_VELOCITY.length()*1.5)

        if velocity_vector.length() >= MAX_PLAYER_VELOCITY.length():
            velocity_vector = velocity_vector.normalize() * MAX_PLAYER_VELOCITY.length()

        player.velocity += velocity_vector

    def update_position(self, player: Player, dt: float) -> None:
        """Met à jour la position du joueur en fonction de sa vitesse."""
        bonus_modifier = 1
        if isinstance(player.bonus, BonusSpeed) and player.bonus.active:
            bonus_modifier = 3

        player.position += player.velocity * dt * bonus_modifier

    def apply_friction(self, player: Player, dt: float) -> None:
        """Applique la friction du sol à un joueur."""
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            player.velocity *= exp(-(GROUND_ICE_FRICTION / BALL_MASS) * dt)
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
            self.level.game.sound_manager.play_sound(SOUNDS["water"])
            player.velocity = Vector(0.0, 0.0)
            self.level.map.teleportPlayerToSpawn(player)
            print(f"Player:{player.name} is out of bounds")
            self.level.centerOnPlayer(player)

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
            self.level.game.sound_manager.play_sound(SOUNDS["victory"])

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


        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return


        original_velocity = player.velocity.copy()
        original_position = player.position.copy()


        intersection = player.rect.clip(tile.rect)

        # Calculate penetration
        pen_x = intersection.width
        pen_y = intersection.height

        if pen_x == 0 and pen_y == 0:
            return

        # Calculs par face
        dist_left = abs(player.rect.right - tile.rect.left)
        dist_right = abs(player.rect.left - tile.rect.right)
        dist_top = abs(player.rect.bottom - tile.rect.top)
        dist_bottom = abs(player.rect.top - tile.rect.bottom)

        min_dist = min(dist_left, dist_right, dist_top, dist_bottom)


        normal = Vector(0, 0)
        collision_type = ""

        buffer = 1.0

        # Résolution basé sur la face
        if min_dist == dist_left:
            player.position.x = tile.rect.left - player.radius - buffer
            player.velocity.x = -abs(player.velocity.x)  # Ensure velocity is away from tile
            normal = Vector(-1, 0)
            collision_type = "left edge"

        elif min_dist == dist_right:
            player.position.x = tile.rect.right + player.radius + buffer
            player.velocity.x = abs(player.velocity.x)  # Ensure velocity is away from tile
            normal = Vector(1, 0)
            collision_type = "right edge"

        elif min_dist == dist_top:
            player.position.y = tile.rect.top - player.radius - buffer
            player.velocity.y = -abs(player.velocity.y)  # Ensure velocity is away from tile
            normal = Vector(0, -1)
            collision_type = "top edge"

        elif min_dist == dist_bottom:
            player.position.y = tile.rect.bottom + player.radius + buffer
            player.velocity.y = abs(player.velocity.y)  # Ensure velocity is away from tile
            normal = Vector(0, 1)
            collision_type = "bottom edge"

        min_escape_velocity = 20.0

        # Vérification speed minimul sinon cancel pour éviter double hits
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
            player.velocity *= (max_collision_speed / current_speed) * .8 # speed redistribution

        # IMPORTANT: Update the rect position after changing the player position
        player.rect.x = int(player.position.x)
        player.rect.y = int(player.position.y)

        if DEBUG_MODE:
            print(f"Collision: {player.name} hit {collision_type} - Pen X: {pen_x}, Pen Y: {pen_y}")
            print(
                f"  Original pos: ({original_position.x:.1f}, {original_position.y:.1f}) → New pos: ({player.position.x:.1f}, {player.position.y:.1f})")
            print(
                f"  Original vel: ({original_velocity.x:.1f}, {original_velocity.y:.1f}) → New vel: ({player.velocity.x:.1f}, {player.velocity.y:.1f})")

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

        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return

        intersection = player.rect.clip(tile.rect)
        self.level.game.sound_manager.play_sound(SOUNDS["bounce"])

        # On calcule les superpositions sur X et Y
        pen_x = intersection.width
        pen_y = intersection.height

        # Variation aléatoire de l'angle (± 1 degré)
        angle_variation = random.uniform(-1, 1) * (math.pi / 180)  # Conversion degrés -> radians

        # Résolution de la collision en X
        if pen_x < pen_y:
            if player.rect.centerx < tile.rect.centerx:
                # Le joueur est à gauche de la tile, on le décale vers la gauche
                player.position.x -= pen_x
            else:
                # Le joueur est à droite de la tile, on le décale vers la droite
                player.position.x += pen_x

            # On inverse la vélocité en X avec une légère variation d'angle
            vx = -2 * player.velocity.x
            vy = player.velocity.y

            # Calcul de l'amplitude et de l'angle actuel
            speed = math.sqrt(vx ** 2 + vy ** 2)
            angle = math.atan2(vy, vx)

            # Application de la variation d'angle
            angle += angle_variation

            # Recalcul des composantes de la vélocité
            player.velocity.x = speed * math.cos(angle)
            player.velocity.y = speed * math.sin(angle)

        # Résolution de la collision en Y
        else:
            if player.rect.centery < tile.rect.centery:
                # Le joueur est au-dessus de la tile, on le décale vers le haut
                player.position.y -= pen_y
            else:
                # Le joueur est en dessous de la tile, on le décale vers le bas
                player.position.y += pen_y

            # On inverse la vélocité en Y avec une légère variation d'angle
            vx = player.velocity.x
            vy = -2 * player.velocity.y

            # Calcul de l'amplitude et de l'angle actuel
            speed = math.sqrt(vx ** 2 + vy ** 2)
            angle = math.atan2(vy, vx)

            # Application de la variation d'angle
            angle += angle_variation

            # Recalcul des composantes de la vélocité
            player.velocity.x = speed * math.cos(angle)
            player.velocity.y = speed * math.sin(angle)

    def resolve_player_speed_right(self, player: Player) -> None:
        """
        Accelere le joueur vers la droite
        """
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return

        self.level.game.sound_manager.play_sound(SOUNDS["boost"])
        if player.velocity.x > 0:
            player.velocity.x = player.velocity.x * 1.1
        else :
            player.velocity.x = player.velocity.x * 0.9 + 10

    def resolve_player_speed_left(self, player: Player) -> None:
        """
        Accelere le joueur vers la gauche
        """
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return

        self.level.game.sound_manager.play_sound(SOUNDS["boost"])
        if player.velocity.x > 0:
            player.velocity.x = player.velocity.x * 0.9 - 10
        else :
            player.velocity.x = player.velocity.x * 1.1

    def resolve_player_speed_down(self, player: Player) -> None:
        """
        Accelere le joueur vers le bas
        """
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return

        self.level.game.sound_manager.play_sound(SOUNDS["boost"])
        if player.velocity.y > 0:
            player.velocity.y = player.velocity.y * 1.1
        else :
            player.velocity.y = player.velocity.y * 0.9 + 10

    def resolve_player_speed_up(self, player: Player) -> None:
        """
        Accelere le joueur vers le haut
        """
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return

        self.level.game.sound_manager.play_sound(SOUNDS["boost"])
        if player.velocity.y > 0:
            player.velocity.y = player.velocity.y * 0.9 - 10
        else :
            player.velocity.y = player.velocity.y * 1.1

    def update(self, dt: float) -> None:
        """Met à jour la physique du jeu pour tous les joueurs avec un système de collision robuste."""

        for player in self.players:
            if player.finished:
                continue

            #limitation de vitesse
            if not isinstance(player.bonus,BonusSpeed):
                max_velocity = 1200
                player.velocity.x = max(-max_velocity, min(player.velocity.x, max_velocity))
                player.velocity.y = max(-max_velocity, min(player.velocity.y, max_velocity))


            # Mise à jour de la position du joueur
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

                    elif tile.id == "Bounce" and player.rect.colliderect(tile.rect):
                        self.resolve_player_bounce_collision(player, tile)
                        collision_detected = True

                    elif tile.id == "Speed_right" and player.rect.colliderect(tile.rect):
                        self.resolve_player_speed_right(player)
                        collision_detected = True

                    elif tile.id == "Speed_left" and player.rect.colliderect(tile.rect):
                        self.resolve_player_speed_left(player)
                        collision_detected = True

                    elif tile.id == "Speed_down" and player.rect.colliderect(tile.rect):
                        self.resolve_player_speed_down(player)
                        collision_detected = True

                    elif tile.id == "Speed_up" and player.rect.colliderect(tile.rect):
                        self.resolve_player_speed_up(player)
                        collision_detected = True
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
