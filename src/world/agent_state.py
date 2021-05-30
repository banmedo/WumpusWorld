from copy import copy

from src.world.config import MOVEMOD
from src.world.utils import clamp

class AgentState:
    """This is the state of Agent that will be represented in the 
    environment. His goal is to pick up the gold and climb out.
    """
    # The names mapping array of facing to directions
    __DIRECTIONS = ["N", "E", "S", "W"]
    
    # starting parameters for a new agent
    rem_arrows = 1
    has_gold = False
    is_alive = True
    location = [0,0]
    facing = 1

    # get a copy agent with specific overriding parameter
    def __copy(self,
               rem_arrows=None,
               has_gold=None,
               is_alive=None,
               location=None,
               facing=None):
        new = copy(self)
        if (rem_arrows is not None):
            new.rem_arrows = rem_arrows
        if (has_gold is not None):
            new.has_gold = has_gold
        if (is_alive is not None):
            new.is_alive = is_alive
        if (location is not None):
            new.location = location
        if (facing is not None):
            new.facing = facing
        return new

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
        return self.__copy(facing=facing)
    
    # turn the agent right
    def turn_right(self):
        facing = self.facing + 1
        if (facing > 3):
            facing = 0
        return self.__copy(facing=facing)
        

    # move the agent forward
    def move_forward(self, X, Y):
        move_vector = MOVEMOD[self.get_direction()]
        move_from = self.location
        new_location = [
            clamp(move_from[0]+move_vector[0], 0, X - 1), 
            clamp(move_from[1]+move_vector[1], 0, Y - 1)
        ]
        return self.__copy(location=new_location)

    # use an arrow 
    def use_arrow(self):
        return self.__copy(rem_arrows=max(0, self.rem_arrows-1))
        
    # perform an action
    def act(self, action, X, Y):
        if action == "turn_left":
            return self.turn_left()
        elif action == "turn_right":
            return self.turn_right()
        elif action == "forward":
            return self.move_forward(X, Y)
        elif action == "shoot":
            return self.use_arrow()
        else:
            return self

    # show current state of agent
    def __str__(self):
        return "location: {0}, direction: {1}, has_gold: {2}, arrows: {3}, is_alive: {4}"\
            .format(self.location, 
                    self.get_direction(), 
                    self.has_gold, 
                    self.rem_arrows, 
                    self.is_alive)
