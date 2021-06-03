import sys
sys.path.insert(0, "../..")

from src.world.agent import Agent
from src.world.environment import Environment
from src.world.utils import rand_index

class NaiveAgent(Agent):
    ACTIONS = ["forward","turn_left","turn_right","grab","shoot","climb"]

    def next_action(self, _):
        return self.ACTIONS[rand_index(len(self.ACTIONS))]
