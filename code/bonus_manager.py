import random
import time

import pygame

import settings
from broadcast import BroadcastManager
from player import Player

# Dev vars
RESPAWN = False
RESPAWN_TIME = 15  # time in seconds

EXPLOSION_MAX_POWER = 2


class BonusType:
    def __init__(self, name: str, color: str, icon_id: int):
        self.name = name
        self.color = color
        self.icon_id = icon_id
        self.broadcast = BroadcastManager()

    def apply_bonus(self, player: Player, players: [Player]) -> None:
        """
        :param player:
        :param players: Players does contain the players who finished and the player of ':param player'
        """
        raise NotImplementedError("This method isn't implemented in this class")

    def consume_bonus(self, player: Player, players: [Player]) -> None:
        """

        :param player:
        :param players: Players does contain the players who finished and the player of ':param player'
        """
        pass

    def update(self, surface: pygame.Surface, x, y):
        self.broadcast.draw(surface)
        self.draw_bonus(surface, x, y)

    def show_pickup_message(self) -> None:
        """
        Generic message when bonus picked up
        """
        self.broadcast.change_color(self.color)
        self.broadcast.change_time(5)
        self.broadcast.broadcast(f"Vous avez récupéré {self.name} !")

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
    def __init__(self):
        super().__init__("BonusSpeed", "green", 0)

    def apply_bonus(self, player: Player, players: [Player]) -> None:
        player.bonus = self

    def consume_bonus(self, player: Player, players: [Player]) -> None:
        player.bonus = None

    def show_usage_message(self) -> None:
        self.broadcast.change_color(self.color)
        self.broadcast.change_color(1)
        self.broadcast.broadcast("Vous avez ce bonus de vitesse jusqu'à la fin de ce tour !")


class BonusExplosion(BonusType):
    def __init__(self):
        super().__init__("BonusExplosion", "red", 1)

    def apply_bonus(self, player: Player, players: [Player]) -> None:
        player.bonus = self

    def consume_bonus(self, player: Player, players: [Player]) -> None:
        for target in players:
            if target == player or target.hide:
                continue
            diff = player.position - target.position
            multiplier = min((1 / max(diff.length(),0.001)), EXPLOSION_MAX_POWER)
            repulsion = diff.normalize() * multiplier * 100
            if settings.DEBUG_MODE: print(f"[DEBUG] PRE {target.name} : {target.position} : {target.velocity}")
            target.velocity -= repulsion * 1000
            if settings.DEBUG_MODE: print(f"[DEBUG] POS {target.name} : {target.position} : {target.velocity}")
        player.bonus = None


    def show_usage_message(self) -> None:
        self.broadcast.change_color(self.color)
        self.broadcast.change_color(1)
        self.broadcast.broadcast("Appuyez sur 'E' pour utiliser le bonus d'explosion !")


class Bonus:
    def __init__(self, obj) -> None:

        if obj.name != "bonus":
            raise Exception("This object can't be used to construct a Bonus class, object name must be 'bonus'")

        self.x = obj.x
        self.y = obj.y

        self.bonus = get_random_bonus()

        self.available = True
        self.last_pick = 0

    def pick_bonus(self, player: Player, players: [Player]) -> None:
        if not self.available or isinstance(player.bonus, BonusType):
            return

        self.available = False
        self.last_pick = time.time()

        self.bonus.show_pickup_message()
        self.bonus.apply_bonus(player, players)

    def update_bonus(self, surface: pygame.Surface) -> None:
        self.bonus.update(surface, self.x, self.y)
        if not self.available and time.time() - self.last_pick > RESPAWN_TIME:
            self.respawn_bonus()

    def respawn_bonus(self) -> None:
        self.bonus = get_random_bonus()
        self.available = True
        self.last_pick = 0
        #TODO: Make animation on respawn

    def draw_bonus(self, surface: pygame.Surface):
        if self.available:
            self.bonus.draw_bonus(surface, self.x, self.y)

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


BonusList = [BonusExplosion]


def get_random_bonus() -> BonusType:
    return random.choice(BonusList)()
