import random
import time

import pygame

from settings import OVERLAY_MENU_MARGIN, SOUNDS
from gif_manager import Gif
import settings
from broadcast import BroadcastManager
from player import Player
from sound import SoundManager

# Dev vars
RESPAWN = False
RESPAWN_TIME = 15  # temps en sec

EXPLOSION_MAX_POWER = 1


class BonusType:
    def __init__(self, name: str, color: str, icon_id: str, broadcast_manager:BroadcastManager):
        self.name = name
        self.color = color
        self.icon_id = icon_id
        self.broadcast_manager = broadcast_manager
        self.gif = Gif(icon_id, OVERLAY_MENU_MARGIN, OVERLAY_MENU_MARGIN, .05, False, False)
        self.sound = SoundManager()

    def apply_bonus(self, player: Player, players: [Player]) -> None:
        """
        :param player:
        :param players: Players does contain the players who finished and the player of ':param player'
        """
        raise NotImplementedError("This method isn't implemented in this class")

    def consume_bonus(self, player: Player, players: [Player], overlay:pygame.Surface) -> None:
        """

        :param overlay:
        :param player:
        :param players: Players does contain the players who finished and the player of ':param player'
        """
        pass

    def update(self, surface: pygame.Surface, x, y):
        #self.broadcast.draw(surface)
        self.draw_bonus(surface, x, y)

    def show_pickup_message(self) -> None:
        """
        Generic message when bonus picked up
        """
        self.broadcast_manager.broadcast(f"Vous avez récupéré {self.name} !")

    def show_usage_message(self) -> None:
        """
        Custom message how to use the bonus
        """
        pass

    def draw_bonus(self, surface: pygame.Surface, x, y):
        if settings.DEBUG_MODE:
            pygame.draw.circle(
                surface=surface,
                color=pygame.Color(self.color),
                center=(x, y),
                radius=20
            )


class BonusSpeed(BonusType):
    def __init__(self, broadcast_manager:BroadcastManager):
        super().__init__("BonusSpeed", "green", "../asset/GIF/Bonus_vitesse.gif", broadcast_manager)
        self.active = False

    def apply_bonus(self, player: Player, players: [Player]) -> None:
        player.bonus = self

    def consume_bonus(self, player: Player, players: [Player], overlay:pygame.Surface) -> None:
        self.active = True
        self.show_usage_message()
        self.sound.play_sound(SOUNDS["clic"])

    def next_turn(self, player:Player):
        if self.active:
            self.active = False
            player.bonus = None
            self.broadcast_manager.broadcast("Vous n'avez plus de bonus de vitesse !")

    def show_usage_message(self) -> None:
        self.broadcast_manager.broadcast("Vous avez ce bonus de vitesse jusqu'à la fin de ce tour !")

class BonusExplosion(BonusType):
    def __init__(self, broadcast_manager:BroadcastManager):
        super().__init__("BonusExplosion", "red", "../asset/GIF/malus_explosion.gif", broadcast_manager)
        self.active = False
        self.start_time = -1
        self.end_time = -1

    def apply_bonus(self, player: Player, players: [Player]) -> None:
        player.bonus = self

    def consume_bonus(self, player: Player, players: [Player], overlay:pygame.Surface) -> None:

        self.active = True
        self.sound.play_sound(SOUNDS["clic"])

        player_pos = player.position
        MAX_REPULSION_DISTANCE = 500
        EXPLOSION_MAX_POWER = 10
        REPULSION_FORCE = 750

        for target in players:
            if target == player or target.hide:
                continue

            diff_x = player_pos.x - target.position.x
            diff_y = player_pos.y - target.position.y

            square_dist = diff_x * diff_x + diff_y * diff_y
            if square_dist > MAX_REPULSION_DISTANCE * MAX_REPULSION_DISTANCE:
                continue

            distance = square_dist ** 0.5  # sqrt

            if distance < 0.1:
                multiplier = EXPLOSION_MAX_POWER
            else:
                multiplier = min((1 / distance), EXPLOSION_MAX_POWER)

            if multiplier > 0:
                if distance > 0:
                    norm_x = diff_x / distance
                    norm_y = diff_y / distance
                else:
                    norm_x, norm_y = 1.0, 0.0

                # Clalcul repulsion vector
                repulsion_x = norm_x * multiplier * 100
                repulsion_y = norm_y * multiplier * 100

                # Apply vecteur
                target.velocity.x -= repulsion_x * REPULSION_FORCE
                target.velocity.y -= repulsion_y * REPULSION_FORCE


    def show_usage_message(self) -> None:
        self.broadcast_manager.broadcast("Appuyez sur 'E' pour utiliser le bonus d'explosion !")

class BonusFantome(BonusType):
    def __init__(self, broadcast_manager:BroadcastManager):
        super().__init__("BonusFantome", "blue", "../asset/GIF/Bonus_invisible.gif", broadcast_manager)
        self.active = False

    def apply_bonus(self, player: Player, players: [Player]) -> None:
        player.bonus = self

    def consume_bonus(self, player: Player, players: [Player], overlay:pygame.Surface) -> None:
        self.active = True
        self.show_usage_message()
        self.sound.play_sound(SOUNDS["clic"])

    def next_turn(self,player: Player):
        if self.active:
            self.active = False
            player.bonus = None
            self.broadcast_manager.broadcast("Vous n'êtes plus invisible !")

    def show_usage_message(self) -> None:
        self.broadcast_manager.broadcast("Vous êtes maintenant invisible !")

class BonusAimant(BonusType):
    def __init__(self, broadcast_manager:BroadcastManager):
        super().__init__("BonusAimant", "yellow", "../asset/GIF/Bonus_aimant.gif", broadcast_manager)
        self.active = False
        self.start_time = -1

    def isActive(self):
        if time.time() - self.start_time > 5:
            self.active = False
        return self.active

    def apply_bonus(self, player: Player, players: [Player]) -> None:
        player.bonus = self

    def consume_bonus(self, player: Player, players: [Player], overlay:pygame.Surface) -> None:
        if not self.active:
            self.active = True
            self.sound.play_sound(SOUNDS["magnet"])
            self.start_time = time.time()

    def next_turn(self,player: Player):
        if self.start_time != -1:
            player.bonus = None

    def show_usage_message(self) -> None:
        self.broadcast_manager.broadcast("Appuyez sur 'E' pour utiliser le bonus d'aimant pendant ce tour !")


class Bonus:
    def __init__(self, obj, broadcast:BroadcastManager) -> None:

        if obj.name != "bonus":
            raise Exception("This object can't be used to construct a Bonus class, object name must be 'bonus'")

        self.broadcast = broadcast
        self.x = obj.x
        self.y = obj.y

        self.bonus = BonusAimant(self.broadcast)#random.choice(BonusList)(self.broadcast)

        self.available = True
        self.last_pick = 0

        self.gif = Gif("../asset/GIF/Bonus_V1.2.gif",self.x-40,self.y-40,.05,True,False)

    def pick_bonus(self, player: Player, players: [Player]) -> None:
        if not self.available or isinstance(player.bonus, BonusType):
            return

        self.available = False
        self.last_pick = time.time()

        self.bonus.show_pickup_message()
        self.bonus.apply_bonus(player, players)
        self.gif.hide = True

    def update_bonus(self, surface: pygame.Surface) -> None:
        self.bonus.update(surface, self.x, self.y)
        if not self.available and time.time() - self.last_pick > RESPAWN_TIME:
            self.respawn_bonus()

    def respawn_bonus(self) -> None:
        self.bonus = random.choice(BonusList)(self.broadcast) # Chaque slot à bonus à un bonus aléatoire
        self.available = True
        self.last_pick = 0
        self.gif.hide = False

    def draw_bonus(self, surface: pygame.Surface):
        if self.available:
            self.gif.update(surface)

    def print_bonus_log(self):
        print(f"""
Bonus : 
  x : {self.x}
  y : {self.y}
  bonus :
    type : {self.bonus.name} 
    icon_id : {self.bonus.icon_id}
  available : {self.available}
  last_pick : {self.last_pick}
        """)


BonusList = [BonusExplosion,BonusSpeed,BonusAimant, BonusFantome]

