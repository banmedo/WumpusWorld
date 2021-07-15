from copy import copy

from src.world.config import MOVEMOD
from src.world.utils import clamp

class Agent:
    """This is the Agent that will traverse through the environment.
    His goal is to pick up the gold and climb out.
    """
    # The names mapping array of facing to directions
    __DIRECTIONS = ["N", "E", "S", "W"]
    
    def __init__(self):# starting parameters for a new agent
        self.rem_arrows = 1
        self.has_gold = False
        self.is_alive = True
        self.location = [0,0]
        self.facing = 1

    # get agent direction
    def get_direction(self):
        return self.__DIRECTIONS[self.facing]
    
    # check if agent has arrows
    def has_arrows(self):
        return self.rem_arrows > 0

    # turn the agent left
    def turn_left(self):
        facing = self.facing - 1
        if (facing < 0):
            facing = 3
        self.facing = facing
    
    # turn the agent right
    def turn_right(self):
        facing = self.facing + 1
        if (facing > 3):
            facing = 0
        self.facing = facing
        

    # move the agent forward
    def move_forward(self, X, Y):
        move_vector = MOVEMOD[self.get_direction()]
        move_from = self.location
        new_location = [
            clamp(move_from[0]+move_vector[0], 0, X - 1), 
            clamp(move_from[1]+move_vector[1], 0, Y - 1)
        ]
        self.location = new_location
