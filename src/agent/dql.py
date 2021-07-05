import sys
sys.path.insert(0, "../..")

import numpy as np

from src.world.agent import Agent
from src.world.agent_state import AgentState
from src.world.utils import rand_index

class DQLAgent(Agent):
    ACTIONS = ["forward","turn_left","turn_right","grab","shoot","climb"]

    def __init__(self,
                 env,
                 agent_state = AgentState(),
                 ):
        self.X = env.X
        self.Y = env.Y
        self.pit_prob = env.pit_prob
        self.climb_empty = env.climb_empty
        self.agent_state = agent_state

        self.safe_locations = [self.agent_state.location]
        percepts = env.get_percepts(skip_reward=True)
        self.stench_locations = [self.agent_state.location] if percepts.stench else []
        self.breeze_locations = [self.agent_state.location] if percepts.breeze else []

        self.sees_glitter = False
        self.heard_screech = False


    def get_agent_state(self):
        x, y = self.agent_state.location

        # array to show where the location exists
        agent_loc = np.zeros((self.X, self.Y))
        agent_loc[x][y] = 1

        # array to record where agent has been
        agent_visited = np.zeros((self.X, self.Y))
        for x, y in self.safe_locations:
            agent_visited[x][y] = 1
        # array to log all the cells that has breezes
        stenches = np.zeros((self.X, self.Y))
        for x, y in self.stench_locations:
            stenches[x][y] = 1

        # array to log all the cells that has breezes
        breezes = np.zeros((self.X, self.Y))
        for x, y in self.breeze_locations:
            breezes[x][y] = 1
        
        for x in range(self.X):
            for y in range(self.Y):
                agent_visited[x][y] = 1 if [x, y] in self.safe_locations else 0
                stenches[x][y] = 1 if [x, y] in self.stench_locations else 0
                breezes[x][y] = 1 if [x, y] in self.breeze_locations else 0

        agent_facing = [False for _ in range(4)]
        agent_facing[self.agent_state.facing] = True

        has_gold = self.has_gold
        has_arrows = self.has_arrows()
        sees_glitter = self.sees_glitter
        heard_screech = self.heard_screech

        agent_state = [
            *agent_loc.flatten(),
            *agent_facing,
            *agent_visited.flatten(),
            *stenches.flatten(),
            *breezes.flatten(),
            has_gold,
            has_arrows,
            sees_glitter,
            heard_screech
        ]

        return np.array(agent_state).reshape(1, len(agent_state))


    def act(self, action, percepts):
        action = "turn_left"
        self.agent_state.act(action, self.X, self.Y)
        if action == "forward":
            if self.agent_state.location not in self.safe_locations:
                self.safe_locations.append(self.agent_state.location)
        elif action == "grab" and percepts.glitter:
            self.has_gold = True
        self.sees_glitter = percepts.glitter
        self.heard_screech = self.heard_screech or percepts.screech
        return self.get_agent_state()
                

    def next_action(self, percepts):
        return self.ACTIONS[rand_index(len(self.ACTIONS))]
