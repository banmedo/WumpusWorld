class Agent:
    __DIRECTIONS = ["N", "E", "S", "W"]

    arrows = 1
    gold = False
    facing = 1 # possible E, W, N, S 
    alive = True

    def __init__(self, location):
        self.location = location 

    def set_location(self, x, y):
        self.location= [x, y]

    def get_location(self):
        return self.location
        
    def get_arrows(self):
        return self.arrows
    
    def has_gold(self):
        return self.gold

    def get_facing(self):
        return self.facing

    def get_direction(self):
        return self.__DIRECTIONS[self.facing]

    def is_alive(self):
        return self.alive

    def use_arrow(self):
        self.arrows = self.arrows - 1
    
    def pick_gold(self):
        self.gold = True

    def turn_left(self):
        self.facing = self.facing - 1
        if (self.facing < 0):
            self.facing = 3
    
    def turn_right(self):
        self.facing = self.facing + 1
        if (self.facing > 3):
            self.facing = 0

    def kill(self):
        self.alive = False
