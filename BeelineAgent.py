import time
 
from src.config import *
from src.environment import Environment
from src.renderer import Renderer
from src.utils import rand_index, log_world

ACTION_DEPTH = 10
ACTIONS = ["forward","turn_left","turn_right","shoot"]

# start playing the game
def startGame(env):
    log_world("start", env.check_environment(), env)
    for action in range(0, ACTION_DEPTH):
        action = ACTIONS[rand_index(len(ACTIONS))]
        state = env.perform(action)
        log_world(action, state, env)
        if (not state[0] or not state[1]):
            env.end_game()
            break

# set up a new game
def newGame():
    env = Environment(GAME_SETTINGS.SIZE_X, GAME_SETTINGS.SIZE_Y, GAME_SETTINGS.CLIMB_EMPTY, GAME_SETTINGS.PIT_PROB)
    # renderer = Renderer(env)
    # renderer.refresh_world()
    startGame(env)


if __name__ == "__main__":
    newGame()
