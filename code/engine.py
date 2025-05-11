import math
import random
from bonus_manager import BonusSpeed, BonusFantome, BonusAimant
from player import Player
from settings import *
from math import exp, sqrt


class Engine:
    """
    Cette classe gère toutes les lois de la physique, les collisions, et les interactions
    entre les joueurs et le terrain.
    """

    def __init__(self, level):
        self.level = level  # Stocke le niveau actuel
        self.players = level.players  # Liste des joueurs (objets physiques mobiles)
        self.num_players = len(self.players)  # Nombre total de joueurs

    def resolve_shot(self, player: Player, velocity_vector: Vector):
        """
        Applique une impulsion au joueur lorsqu'il frappe la balle.
        Ici: v_finale = v_initiale + impulsion
        Il y'a une limitation de vitesse pour garder le jeu stable.
        """

        # Limitation de la vitesse maximale
        if velocity_vector.length() >= MAX_PLAYER_VELOCITY.length():
            velocity_vector = velocity_vector.normalize() * MAX_PLAYER_VELOCITY.length()

        # Application de l'impulsion: addition vectorielle de la vitesse
        player.velocity += velocity_vector

    def update_position(self, player: Player, dt: float) -> None:
        """
        Met à jour la position du joueur selon l'équation du mouvement: x(t+dt) = x(t) + v·dt
        On utilise la méthode d'Euler explicite
        "dt" représente l'intervalle de temps écoulé depuis la dernière mise à jour (en secondes).
        """
        bonus_modifier = 1  # Facteur multiplicateur normal
        if isinstance(player.bonus, BonusSpeed) and player.bonus.active:
            bonus_modifier = 3  # Triple la vitesse si le bonus de vitesse est actif

        player.position += player.velocity * dt * bonus_modifier

    def apply_friction(self, player: Player, dt: float) -> None:
        """
        Applique une force de frottement qui ralentit le joueur.
        Modèle de friction où la force est proportionnelle à la vitesse: F = -k·v
        Se traduit par une décroissance exponentielle de la vitesse (e^-kt).
        """
        # Cas spécial: sur la glace avec le bonus "fantôme"
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            player.velocity *= exp(-(GROUND_ICE_FRICTION / BALL_MASS) * dt)

        # Récupère le coefficient de friction selon la surface
        friction = self.get_friction_at_point(player.position)

        # Application de la formule exponentielle: v(t) = v0·e^(-kt)
        # Où k = friction/masse
        player.velocity *= exp(-(friction / BALL_MASS) * dt)

    def get_friction_at_point(self, point: tuple[float, float]) -> float:
        """
        Détermine le coefficient de friction à une position donnée selon le type de terrain.
        """
        for tile in self.level.map.tiles:
            if tile.rect.collidepoint(point):
                # Différentes surfaces ont différents coefficients de friction
                if tile.id == "Grass":
                    return GROUND_GRASS_FRICTION  # Herbe: friction moyenne
                elif tile.id == "Sand":
                    return GROUND_SAND_FRICTION  # Sable: friction élevée
                elif tile.id == "Ice":
                    return GROUND_ICE_FRICTION  # Glace: friction faible

        # Par défaut, on considère le joueur sur l'herbe
        return GROUND_GRASS_FRICTION

    def resolve_player_player_collision(self, player1: Player, player2: Player) -> None:
        """
        Résout une collision élastique entre deux joueurs.
        On modélise une collision entre deux sphères de même masse.
        """
        # Pas de collision si l'un des joueurs a déjà terminé
        if player1.finished or player2.finished:
            return

        # Le bonus fantôme permet de traverser les autres joueurs
        if isinstance(player1.bonus, BonusFantome) and player1.bonus.active:
            return

        # Calcul de la distance entre les deux joueurs
        diff = player1.position - player2.position
        distance = diff.length()
        min_distance = player1.radius + player2.radius  # Distance minimale ou il n'y a pas de collision

        if distance < min_distance:
            # Collision détectée si les joueurs se superposent
            # Calcul du vecteur "normmal" dans la direction de la collision
            normal = diff.normalize() if distance != 0 else Vector(1.0, 0.0)

            # Correction de la superposition entre les joueurs
            overlap = min_distance - distance
            player1.position += normal * (overlap / 2)  # Déplace le premier joueur
            player2.position -= normal * (overlap / 2)  # Déplace le second joueur

            # On projette les vitesses sur l'axe de collision
            v1 = player1.velocity.dot(normal)
            v2 = player2.velocity.dot(normal)  # Même chose pour le second joueur

            # Échange des vitesses
            # Pour des masses égales, les vitesses sont échangées
            player1.velocity += normal * (v2 - v1)
            player2.velocity += normal * (v1 - v2)

    def resolve_out_of_bounds(self, player: Player) -> None:
        """
        Gère le cas où un joueur sort des limites de la carte.
        Équivalent à une condition aux limites avec repositionnement.
        """
        # Le bonus fantôme permet de sortir des limites
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return

        if self.is_out_of_bounds(player):
            # Effet sonore pour signaler la sortie
            self.level.game.sound_manager.play_sound(SOUNDS["water"])

            # Arrêt mouvement
            player.velocity = Vector(0.0, 0.0)

            # Téléportation au point de départ
            self.level.map.teleportPlayerToSpawn(player)
            print(f"Joueur:{player.name} est sorti des limites")

            # On recentre la caméra sur le joueur
            self.level.centerOnPlayer(player)

    def is_out_of_bounds(self, player: Player) -> bool:
        """
        Vérifie si un joueur est sorti des limites du terrain.
        """
        for tile in self.level.map.tiles:
            if tile.rect.collidepoint(player.position) and tile.id != "Water":
                return False  # Le joueur est sur une tuile valide
        return True  # Le joueur n'est sur aucune tuile valide, il est "hors limites"

    def resolve_finish(self, player: Player) -> None:
        """
        Gère la fin de partie pour un joueur quand il atteint le trou.
        """
        if not player.finished:
            print(f"Joueur:{player.name} a terminé en x coups")
            # Arrêt complet du mouvement
            player.velocity = Vector(0.0, 0.0)
            player.finished = True
            # Effet sonore de victoire
            self.level.game.sound_manager.play_sound(SOUNDS["victory"])

    def is_on_finish(self, player: Player) -> None:
        """
        Vérifie si un joueur a atteint le trou final.
        Calcul de distance entre le centre du joueur et le trou.
        """
        hole = self.level.map.hole

        # Calcul de la différence de position
        diff_x, diff_y = player.position.x - hole.x, player.position.y - hole.y

        # Calcul de la distance avec Pythagore
        distance = sqrt(diff_x ** 2 + diff_y ** 2)

        # Si la distance est inférieure au rayon de la balle
        if distance < (BALL_RADIUS + 1):
            self.resolve_finish(player)

    def resolve_player_obstacle_collision(self, player: Player, tile) -> None:
        """
        Résolution (améliorée) des collisions joueur-obstacle.
        """
        # Le bonus fantôme permet de traverser les obstacles
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return

        # Sauvegarde de l'état avant collision
        original_velocity = player.velocity.copy()
        original_position = player.position.copy()

        # Calcul de l'intersection entre rectangle du joueur et celui de l'obstacle
        intersection = player.rect.clip(tile.rect)

        # Calcul de la pénétration joueur-obstacle
        pen_x = intersection.width
        pen_y = intersection.height

        if pen_x == 0 and pen_y == 0:
            return  # Pas d'intersection, donc pas de collision

        # Calcul de la distance du joueur à chaque face de l'obstacle
        dist_left = abs(player.rect.right - tile.rect.left)
        dist_right = abs(player.rect.left - tile.rect.right)
        dist_top = abs(player.rect.bottom - tile.rect.top)
        dist_bottom = abs(player.rect.top - tile.rect.bottom)

        # On détermine la face la plus proche
        min_dist = min(dist_left, dist_right, dist_top, dist_bottom)

        normal = Vector(0, 0)  # Vecteur normal à la surface de collision
        collision_type = ""  # Type de collision (pour debug)

        buffer = 1.0  # Petite marge pour éviter les collisions répétées

        # Résolution de la collision selon la face la plus proche
        # Pour chaque cas: on repositionne + on inverse la vitesse normale à la surface
        if min_dist == dist_left:
            # Collision avec le bord gauche de l'obstacle
            player.position.x = tile.rect.left - player.radius - buffer
            player.velocity.x = -abs(player.velocity.x)  # vitesse vers la gauche
            normal = Vector(-1, 0)
            collision_type = "left edge"

        elif min_dist == dist_right:
            # Collision avec le bord droit de l'obstacle
            player.position.x = tile.rect.right + player.radius + buffer
            player.velocity.x = abs(player.velocity.x)  # vitesse vers la droite
            normal = Vector(1, 0)
            collision_type = "right edge"

        elif min_dist == dist_top:
            # Collision avec le bord supérieur de l'obstacle
            player.position.y = tile.rect.top - player.radius - buffer
            player.velocity.y = -abs(player.velocity.y)  # vitesse vers le haut
            normal = Vector(0, -1)
            collision_type = "top edge"

        elif min_dist == dist_bottom:
            # Collision avec le bord inférieur de l'obstacle
            player.position.y = tile.rect.bottom + player.radius + buffer
            player.velocity.y = abs(player.velocity.y)  # vitesse vers le bas
            normal = Vector(0, 1)
            collision_type = "bottom edge"

        # On donne une vitesse minimale après collision pour éviter que le joueur reste "collé"
        min_escape_velocity = 20.0

        # Vitesse pour s'éloigner de l'obstacle
        if normal.x != 0:
            if abs(player.velocity.x) < min_escape_velocity:
                player.velocity.x = normal.x * min_escape_velocity

        if normal.y != 0:
            if abs(player.velocity.y) < min_escape_velocity:
                player.velocity.y = normal.y * min_escape_velocity

        # Limitation de la vitesse après collision pour éviter les accélérations excessives
        max_collision_speed = MAX_PLAYER_VELOCITY.length()
        current_speed = player.velocity.length()

        if current_speed > max_collision_speed:
            # Normalisation de la vitesse à 80% de la vitesse maximale
            player.velocity *= (max_collision_speed / current_speed) * .8  # redistribution de la vitesse

        # IMPORTANT: on update l'affichage du joueur
        player.update()

        # Informations de debug
        if DEBUG_MODE:
            print(f"Collision: {player.name} a touché {collision_type} - Pen X: {pen_x}, Pen Y: {pen_y}")
            print(
                f"  Position originale: ({original_position.x:.1f}, {original_position.y:.1f}) → Nouvelle position: ({player.position.x:.1f}, {player.position.y:.1f})")
            print(
                f"  Vitesse originale: ({original_velocity.x:.1f}, {original_velocity.y:.1f}) → Nouvelle vitesse: ({player.velocity.x:.1f}, {player.velocity.y:.1f})")

            if not hasattr(self.level, 'debug_collisions'):
                self.level.debug_collisions = []

            self.level.debug_collisions.append({
                'position': original_position,
                'normal': normal,
                'velocity': player.velocity.copy(),
                'original_velocity': original_velocity,
                'time': pygame.time.get_ticks(),
            })

    def resolve_bonus(self):
        """
        Vérifie et active les bonus lorsqu'un joueur passe dessus.
        """
        for player in self.players:
            for bonus in self.level.map.bonuses:
                # Calcul de la distance entre le joueur et le bonus
                diff_x, diff_y = player.position.x - bonus.x, player.position.y - bonus.y

                # Utilisation de la distance euclidienne
                distance = sqrt(diff_x ** 2 + diff_y ** 2)

                # Si le joueur est suffisamment proche et que le bonus est disponible
                if distance < (BALL_RADIUS + 5) and bonus.available:
                    bonus.pick_bonus(player, self.players)

    def resolve_player_bounce_collision(self, player: Player, tile) -> None:
        """
        Gère la collision entre un joueur et une tuile bumper (ressort).
        On simule un rebond avec une amplification de la vitesse.
        """
        # Le bonus fantôme permet de traverser les bumpers
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return

        # Calcul de l'intersection
        intersection = player.rect.clip(tile.rect)

        # Effet sonore de rebond
        self.level.game.sound_manager.play_sound(SOUNDS["bounce"])

        # Calcul des superpositions sur les deux axes
        pen_x = intersection.width
        pen_y = intersection.height

        # Variation aléatoire de l'angle (± 1 degré)
        angle_variation = random.uniform(-1, 1) * (math.pi / 180)  # Conversion degrés -> radians

        # Résolution de la collision en X
        if pen_x < pen_y:
            # Collision horizontale
            if player.rect.centerx < tile.rect.centerx:
                # Joueur à gauche du bumper
                player.position.x -= pen_x
            else:
                # Joueur à droite du bumper
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

        else:
            # Collision verticale
            if player.rect.centery < tile.rect.centery:
                # Joueur au-dessus du bumper
                player.position.y -= pen_y
            else:
                # Joueur en dessous du bumper
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
        Accélère le joueur vers la droite.
        """
        # Le bonus fantôme empêche l'effet d'accélération
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return

        # Effet sonore de boost
        self.level.game.sound_manager.play_sound(SOUNDS["boost"])

        if player.velocity.x > 0:
            # Si déjà en mouvement vers la droite, amplifie la vitesse
            player.velocity.x = player.velocity.x * 1.1
        else:
            # Si en mouvement vers la gauche, réduit cette composante et ajoute une impulsion vers la droite
            player.velocity.x = player.velocity.x * 0.9 + 10

    def resolve_player_speed_left(self, player: Player) -> None:
        """
        Accélère le joueur vers la gauche.
        """
        # Le bonus fantôme empêche l'effet d'accélération
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return

        # Effet sonore de boost
        self.level.game.sound_manager.play_sound(SOUNDS["boost"])

        if player.velocity.x > 0:
            # Si en mouvement vers la droite, réduit cette composante et ajoute une impulsion vers la gauche
            player.velocity.x = player.velocity.x * 0.9 - 10
        else:
            # Si déjà en mouvement vers la gauche, amplifie la vitesse
            player.velocity.x = player.velocity.x * 1.1

    def resolve_player_speed_down(self, player: Player) -> None:
        """
        Accélère le joueur vers le bas.
        """
        # Le bonus fantôme empêche l'effet d'accélération
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return

        # Effet sonore de boost
        self.level.game.sound_manager.play_sound(SOUNDS["boost"])

        if player.velocity.y > 0:
            # Si déjà en mouvement vers le bas, amplifie la vitesse
            player.velocity.y = player.velocity.y * 1.1
        else:
            # Si en mouvement vers le haut, réduit cette composante et ajoute une impulsion vers le bas
            player.velocity.y = player.velocity.y * 0.9 + 10

    def resolve_player_speed_up(self, player: Player) -> None:
        """
        Accélère le joueur vers le haut.
        """
        # Le bonus fantôme empêche l'effet d'accélération
        if isinstance(player.bonus, BonusFantome) and player.bonus.active:
            return

        # Effet sonore de boost
        self.level.game.sound_manager.play_sound(SOUNDS["boost"])

        if player.velocity.y > 0:
            # Si en mouvement vers le bas, réduit cette composante et ajoute une impulsion vers le haut
            player.velocity.y = player.velocity.y * 0.9 - 10
        else:
            # Si déjà en mouvement vers le haut, amplifie la vitesse
            player.velocity.y = player.velocity.y * 1.1

    def update(self, dt: float) -> None:
        """
        Fonction principale qui met à jour la physique du jeu pour tous les joueurs.
        """

        for player in self.players:
            # Si le joueur a terminé, on ignore ses calculs physiques
            if player.finished:
                continue

            #limitation de vitesse
            if not isinstance(player.bonus,BonusSpeed) and player.bonus.active:
                max_velocity = 1200
            else:
                max_velocity = 2500

            player.velocity.x = max(-max_velocity, min(player.velocity.x, max_velocity))
            player.velocity.y = max(-max_velocity, min(player.velocity.y, max_velocity))

            # 1. Mise à jour de la position
            # et application des forces de friction
            self.update_position(player, dt)
            self.apply_friction(player, dt)

            # Application du bonus aimant s'il est actif
            # Ce bonus attire le joueur vers le trou final
            if isinstance(player.bonus, BonusAimant) and player.bonus.isActive():
                self.apply_bonus_aimant(player)

            # Mise à jour du rectangle de collision du joueur
            player.update()

            # 2. Vérification des bonus à ramasser
            self.resolve_bonus()

            # 3. Gestion des collisions avec les tuiles
            collision_detected = True
            max_iterations = 3  # Limite le nombre de tentatives pour éviter les boucles infinies
            iterations = 0

            # Boucle de résolution des collisions (plusieurs passes possibles)
            while collision_detected and iterations < max_iterations:
                iterations += 1
                collision_detected = False

                # Traitement des collisions avec obstacles
                for tile in self.level.map.tiles:
                    # Collision avec obstacle (bord de map)
                    if tile.id == "Collision" and player.rect.colliderect(tile.rect):
                        self.resolve_player_obstacle_collision(player, tile)
                        collision_detected = True
                        # Mise à jour du rectangle du joueur
                        player.update()

                    # Collision avec bumper (ressort)
                    elif tile.id == "Bounce" and player.rect.colliderect(tile.rect):
                        self.resolve_player_bounce_collision(player, tile)
                        collision_detected = True

                    # Collision avec accélérateur vers la droite
                    elif tile.id == "Speed_right" and player.rect.colliderect(tile.rect):
                        self.resolve_player_speed_right(player)
                        collision_detected = True

                    # Collision avec accélérateur vers la gauche
                    elif tile.id == "Speed_left" and player.rect.colliderect(tile.rect):
                        self.resolve_player_speed_left(player)
                        collision_detected = True

                    # Collision avec accélérateur vers le bas
                    elif tile.id == "Speed_down" and player.rect.colliderect(tile.rect):
                        self.resolve_player_speed_down(player)
                        collision_detected = True

                    # Collision avec accélérateur vers le haut
                    elif tile.id == "Speed_up" and player.rect.colliderect(tile.rect):
                        self.resolve_player_speed_up(player)
                        collision_detected = True

                player.update()

            # Si atteint nombre max d'itérations, le joueur pourrait être bloqué
            if iterations == max_iterations and collision_detected:
                # Application d'une petite impulsion aléatoire pour aider à sortir de cette situation
                import random
                player.velocity.x += random.uniform(-50, 50)
                player.velocity.y += random.uniform(-50, 50)
                player.update()

            # 4. On vérifie que le joueur est sur la map et s'il à terminé
            self.resolve_out_of_bounds(player)  # Vérifie si le joueur est sorti du terrain
            self.is_on_finish(player)  # Vérifie si le joueur a atteint le trou

        # 5. Gestion des collisions entre joueurs
        for i in range(len(self.players)):
            for j in range(i + 1, len(self.players)):
                self.resolve_player_player_collision(self.players[i], self.players[j])

        # 6. Mise à jour finale des joueurs
        for player in self.players:
            player.update()

    def apply_bonus_aimant(self, player: Player):
        """
        Applique le bonus d'aimant qui attire le joueur vers le trou.
        """
        # Position du trou (cible de l'attraction)
        hole_x, hole_y = self.level.map.hole.x, self.level.map.hole.y
        hole = pygame.math.Vector2(hole_x, hole_y)
        pos = player.position  # Position actuelle du joueur

        # Calcul du vecteur direction vers le trou
        direction = hole - pos

        # La force d'attraction est inversement proportionnelle à la distance
        # (plus proche = force plus intense)
        attraction_force = direction.normalize() * (1 / max(direction.length(), 0.001) * 5) * 100

        # Application de la force
        player.velocity += attraction_force
