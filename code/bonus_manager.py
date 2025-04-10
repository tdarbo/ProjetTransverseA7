import random
import time

import pygame

import settings

from player import Player

# Dev vars
RESPAWN = False
RESPAWN_TIME = 15 # time in seconds

class BonusType:
    def __init__(self, name:str, icon_id:int):
        self.name = name
        self.icon_id = icon_id

    def apply_bonus(self, player:Player, players:[Player]) -> None:
        """

        :param player:
        :param players: Players does contain the players who finished and the player of ':param player'
        """
        raise NotImplementedError("This method isn't implemented in this class")


    def draw_bonus(self, surface:pygame.Surface,x,y):
        if settings.DEBUG_MODE:
            pygame.draw.circle(
                surface=surface,
                color=pygame.Color("green"),
                center=(x,y),
                radius=20
            )



class BonusSpeed(BonusType):
    def __init__(self):
        super().__init__("BonusSpeed", 0)

    def apply_bonus(self, player:Player, players:[Player]) -> None:
        player.speed_bonus = True




class Bonus:
    def __init__(self, obj) -> None:

        if obj.name != "bonus":
            raise Exception("This object can't be used to construct a Bonus class, object name must be 'bonus'")

        self.x = obj.x
        self.y = obj.y

        self.bonus = get_random_bonus()

        self.available = True
        self.last_pick = 0


    def pick_bonus(self, player:Player, players:[Player]) -> None:
        if not self.available:
            return

        self.available = False
        self.last_pick = time.time()

        self.bonus.apply_bonus(player, players)


    def update_bonus(self) -> None:
        if not self.available and time.time() - self.last_pick > RESPAWN_TIME:
            self.respawn_bonus()

    def respawn_bonus(self) -> None:
        self.bonus = get_random_bonus()
        self.available = True
        self.last_pick = 0
        #TODO: Make animation on respawn

    def draw_bonus(self, surface:pygame.Surface):
        if self.available:
            self.bonus.draw_bonus(surface,self.x,self.y)



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

BonusList = [BonusSpeed]

def get_random_bonus() -> BonusType:
    return random.choice(BonusList)()