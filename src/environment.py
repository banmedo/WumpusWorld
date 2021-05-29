import random
from src.percepts import Percepts
from src.config import POINTS

from numpy.core.fromnumeric import size
from src.wumpus import Wumpus
import numpy as np
from .utils import calc_distance, rand_index, rand_prob, clamp

from src.agent import Agent
from src.wumpus import Wumpus


class Environment:
    AGENT_ID = 1
    GOLD_ID = 2
    WUMPUS_ID = 3
    PIT_ID = 4
    GAME_ON = True
    POINTS = 0

    __MOVEMOD = {"N":(0, 1), "E":(1, 0), "S":(0, -1), "W":(-1, 0)}

    def __init__(self, size_x=4, size_y=4, allow_climb=True, pit_prob=0.2):
        self.size_x = size_x
        self.size_y = size_y
        self.pit_prob = pit_prob

        self.start = [0, 0]
        self.gold_loc = [0, 0]
        self.pit_locs = []
        self.allow_climb = allow_climb

        self.agent = Agent(self.start)
        self.wumpus = Wumpus(self.start)
        self.percepts = Percepts()
        self.__build_world()
        

    def __get_random_location(self):
        return [rand_index(self.size_x), rand_index(self.size_y)]

    def __build_world(self):
        agent_location = self.agent.get_location()
        wumpus_location = self.wumpus.get_location()
        while self.gold_loc == agent_location:
            self.gold_loc = self.__get_random_location()

        while wumpus_location == agent_location or wumpus_location == self.gold_loc:
            self.wumpus.set_location(self.__get_random_location())
            wumpus_location = self.wumpus.get_location()

        for x in range(self.size_x):
            for y in range(self.size_y):
                if [x, y] != agent_location:
                    if (rand_prob() <= self.pit_prob):
                        self.pit_locs.append([x, y])
    
    def add_points(self, points):
        self.POINTS = self.POINTS + points

    def get_points(self):
        return self.POINTS

    def get_world_map(self):
        return self.agent.get_location(), self.wumpus.get_location(), self.gold_loc, self.pit_locs

    def perform(self, action):
        self.percepts = Percepts()
        if (action == "forward"):
            self.move_agent_forward()
        elif (action == "turn_left"):
            self.turn_agent_left()
        elif (action == "turn_right"):
            self.turn_agent_right()
        elif (action == "grab"):
            self.grab_gold()
        elif (action == "shoot"):
            self.shoot_arrow()
        elif (action == "climb"):
            self.climb_out()
        self.add_points(POINTS.ACTION)
        return self.check_environment() + [self.get_points()]

    def move_agent_forward(self):
        move_vector = self.__MOVEMOD[self.agent.get_direction()]
        move_from = self.agent.get_location()
        move_to = [move_from[0]+move_vector[0], move_from[1]+move_vector[1]]
        if (move_to[0] >= self.size_y or move_to[0] < 0):
            self.percepts.give_bump()
            move_to[0] = clamp(move_to[0], 0, self.size_y - 1)
        if (move_to[1] >= self.size_x or move_to[1] < 0):
            self.percepts.give_bump()
            move_to[1] = clamp(move_to[1], 0, self.size_y - 1)
        self.agent.set_location(*move_to)

    def turn_agent_left(self):
        self.agent.turn_left()
    
    def turn_agent_right(self):
        self.agent.turn_right()

    def grab_gold(self):
        agent_loc = self.agent.get_location()
        if (not self.agent.has_gold() and agent_loc == self.gold_loc):
            self.agent.pick_gold()

    def shoot_arrow(self):
        if (self.agent.arrows > 0):
            self.agent.use_arrow()
            self.add_points(POINTS.ARROW)
            arrow_loc = self.agent.get_location()
            move_vector = self.__MOVEMOD[self.agent.get_direction()]
            while True:
                arrow_loc = [sum(x) for x in zip(arrow_loc, move_vector)]
                if (arrow_loc == self.wumpus.get_location()):
                    self.wumpus.kill()
                    self.percepts.give_screech()
                    break
                elif (arrow_loc[0] < 0 or arrow_loc[0] >= self.size_x or arrow_loc[1] < 0 or arrow_loc[1] >= self.size_y):
                    break

    def climb_out(self):
        if self.agent.get_location() == self.start:
            if (self.agent.has_gold()):
                self.add_points(POINTS.GOLD)
                self.end_game()
            elif (self.allow_climb):
                self.end_game()


    def is_agent_alive(self):
        agent_loc = self.agent.get_location()
        wumpus_loc = self.wumpus.get_location()
        pits = self.pit_locs

        if ((self.wumpus.is_alive() and agent_loc == wumpus_loc) or agent_loc in pits):
            self.agent.kill()
            self.add_points(POINTS.DEATH)

        if (self.agent.is_alive()):
            return True
        else:
            return False


    def perceive_environments(self):
        agent_loc = self.agent.get_location()
        wumpus_loc = self.wumpus.get_location()
        gold_loc = self.gold_loc
        pits = self.pit_locs

        if (self.agent.has_gold() or agent_loc == gold_loc):
            self.percepts.give_glitter()
        
        wumpus_distance = calc_distance(agent_loc, wumpus_loc)
        if (wumpus_distance <= 1):
            self.percepts.give_stench()

        if (len(pits) > 0):
            pit_distance = [calc_distance(agent_loc, pit) for pit in pits]
            if (min(pit_distance) <= 1):
                self.percepts.give_breeze()
        
        return self.percepts.get_percepts()
        

    def check_environment(self):
        return [self.is_game_on(), self.is_agent_alive()] + self.perceive_environments()

    def end_game(self):
        self.GAME_ON = False

    def is_game_on(self):
        return self.GAME_ON
