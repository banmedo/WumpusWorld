# This file contains the utility/helper functions
import logging
import random

from numpy import sqrt, square
LOG_FILE = "log.log"

logging.basicConfig(filename=LOG_FILE, level=logging.INFO, filemode="w")

def log(message, level=logging.INFO):
    print(message)
    if level == logging.INFO:
        logging.info(message)
    else:
        logging.error(message)

def rand_index(max):
    return random.randint(0, max-1)

def rand_prob():
    return random.uniform(0,1)

def clamp(x, low, high):
    return max(low, min(x, high))

def calc_distance(point_a, point_b):
    return sqrt(square(point_b[0] - point_a[0]) + square(point_b[1] - point_a[1]))

def log_world(action, state, env):
    agent = env.agent.get_location()
    facing = env.agent.get_facing()
    wumpus = env.wumpus.get_location()
    gold = env.gold_loc
    has_gold = env.agent.has_gold()
    pits = env.pit_locs

    world_map = f"{action} - {state} \n"
    for y in reversed(range(0, env.size_y)):
        row = "|"
        for x in range(0, env.size_x):
            loc = [x, y]
            a1 = a2 = a3 = a4 = " "
            if (agent == loc):
                a1 = ["^", ">", "v", "<"][facing]
            if (wumpus == loc):
                a2 = "W"
            if ((has_gold and agent == loc) or (not has_gold and gold == loc)):
                a3 = "G"
            if (loc in pits):
                a4 = "P"
            row = f"{row}{a1}{a2}{a3}{a4}|"
        world_map = world_map+row +"\n"
    log(world_map)
