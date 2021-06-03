from copy import copy

from src.world.config import GAME_SETTINGS
from src.world.utils import get_adjacent_cells, rand_prob, rand_cell_not_origin

from src.world.agent_state import AgentState
from src.world.percepts import Percepts

class Environment:
    # initialize the environment
    def __init__(self,
                 X = GAME_SETTINGS.SIZE_X,
                 Y = GAME_SETTINGS.SIZE_Y,
                 pit_prob = GAME_SETTINGS.PIT_PROB,
                 climb_empty = GAME_SETTINGS.CLIMB_EMPTY,
                 agent = AgentState(),
                 terminated = False,
                 wumpus_alive = True,
                 pit_locations = None,
                 gold_location = None,
                 wumpus_location = None):
        self.X = X
        self.Y = Y
        self.pit_prob = pit_prob
        self.climb_empty = climb_empty
        self.agent = agent
        self.terminated = terminated
        self.wumpus_alive = wumpus_alive
        
        if (pit_locations is not None):
            self.pit_locations = pit_locations
        else:
            pl = []
            for x in range(0,X):
                for y in range(0,Y):
                    if ([x,y]==[0,0]):
                        continue
                    if rand_prob() <= pit_prob:
                        pl.append([x,y])
            self.pit_locations = pl
        
        if (gold_location is not None):
            self.gold_location = gold_location
        else:
            self.gold_location = rand_cell_not_origin(X, Y)
        
        if (wumpus_location is not None):
            self.wumpus_location = wumpus_location
        else:
            self.wumpus_location = rand_cell_not_origin(X, Y)

    # check if pit is at given coords
    def is_pit_at(self, coords):
        return coords in self.pit_locations
    
    # check if wumpus is given coords
    def is_wumpus_at(self, coords):
        return coords == self.wumpus_location
    
    # check if agent is at given coords
    def is_agent_at(self, coords):
        return coords == self.agent.location
    
    # check if there is glitter
    def is_glitter(self):
        return self.gold_location == self.agent.location

    # check if gold is at given coords
    def is_gold_at(self, coords):
        return coords == self.gold_location
    
    # helper function to check if wumpus is in shooting range
    def wumpus_in_range(self, a, w, d):
        if (d == "N"):
            return (w[0] == a[0] and w[1] > a[1])
        elif (d == "E"):
            return (w[0] > a[0] and w[1] == a[1])
        elif (d == "S"):
            return (w[0] == a[0] and w[1] < a[1])
        elif (d == "W"):
            return (w[0] < a[0] and w[1] == a[1])
        else:
            return False

    # check if kill attempt was successful
    def kill_successful(self):
        return self.agent.has_arrows() and \
            self.wumpus_alive and \
            self.wumpus_in_range(
                self.agent.location,
                self.wumpus_location,
                self.agent.get_direction()
            )

    # check if there is a pit next to given coords
    def is_pit_adjacent(self, coords):
        pit_near = False
        adj_cells = get_adjacent_cells(coords)
        for pit in self.pit_locations:
            if pit in adj_cells:
                pit_near = True
        return pit_near or coords in self.pit_locations
    
    # check if wumpus is next to given coords
    def is_wumpus_adjacent(self, coords):
        return self.wumpus_location in get_adjacent_cells(coords) or coords == self.wumpus_location

    # check if there is breeze
    def is_breeze(self):
        return self.is_pit_adjacent(self.agent.location)
    
    # check if there is stench
    def is_stench(self):
        return self.is_wumpus_adjacent(self.agent.location)

    # get current percepts
    def get_percepts(self, skip_reward=False):
        if skip_reward:
            reward = 0
        else:
            reward = -1
        return Percepts(
            stench = self.is_stench(),
            breeze = self.is_breeze(),
            glitter = self.is_glitter(),
            reward = -1
        )

    # act
    def act(self, action):
        if self.terminated:
            return Percept(is_terminated = True)
        else:
            if action == "forward":
                old_loc = self.agent.location
                self.agent.move_forward(self.X, self.Y)
                death = (self.is_wumpus_at(self.agent.location) and self.wumpus_alive) or self.is_pit_at(self.agent.location)
                self.agent.is_alive = not death
                if self.agent.has_gold:
                    gold_location = self.agent.location
                else:
                    gold_location = self.gold_location
                self.gold_location = gold_location
                self.terminated = death
                percepts = self.get_percepts()
                percepts.bump = self.agent.location == old_loc
                percepts.is_terminated = not self.agent.is_alive
                if not self.agent.is_alive:
                    percepts.reward = -1001
                return percepts

            elif action == "turn_left":
                self.agent.turn_left()
                return self.get_percepts()
            
            elif action == "turn_right":
                self.agent.turn_right()
                return self.get_percepts()
            
            elif action == "grab":
                self.agent.has_gold = self.is_glitter()
                return self.get_percepts()

            elif action == "climb":
                in_start = self.agent.location == [0,0]
                success = self.agent.has_gold and in_start
                is_terminated = success or (self.climb_empty and in_start)
                percepts = self.get_percepts()
                percepts.is_terminated = is_terminated
                if success:
                    percepts.reward = 999
                else:
                    percepts.reward = -1
                return percepts
            
            elif action == "shoot":
                had_arrows = self.agent.has_arrows()
                wumpus_killed = self.kill_successful()
                self.agent.use_arrow()
                self.wumpus_alive = self.wumpus_alive and not wumpus_killed
                percepts = self.get_percepts()
                percepts.screech = wumpus_killed
                if (had_arrows):
                    percepts.reward = -11
                return percepts


    def __str__(self):
        agent = self.agent.location
        facing = self.agent.facing
        wumpus = self.wumpus_location
        gold = self.gold_location
        has_gold = self.agent.has_gold
        pits = self.pit_locations

        world_map = "\n"
        for y in reversed(range(0, self.Y)):
            row = "|"
            for x in range(0, self.X):
                loc = [x, y]
                a1 = a2 = a3 = a4 = " "
                if (agent == loc):
                    a1 = ["^", ">", "v", "<"][facing]
                if (wumpus == loc):
                    if (self.wumpus_alive):
                        a2 = "W"
                    else:
                        a2 = "X"
                if ((has_gold and agent == loc) or (not has_gold and gold == loc)):
                    a3 = "G"
                if (loc in pits):
                    a4 = "P"
                row = f"{row}{a1}{a2}{a3}{a4}|"
            world_map = world_map+row +"\n"
        return world_map
