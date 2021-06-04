from src.agent.beeline import BeelineAgent

from src.world.environment import Environment
from src.world.percepts import Percepts

from utils import log

ACTION_DEPTH = 100

def run_episode(env, agent, percept, action_depth=0):
    if (action_depth >= ACTION_DEPTH):
        return 0
    
    next_action = agent.next_action(percept)
    log(f"Action : {next_action}")
    next_percept = env.act(next_action)
    log(env)
    log(next_percept)
    log("------------------------------------------")
    return next_percept.reward + (run_episode(env, agent, next_percept, action_depth+1) if not next_percept.is_terminated else 0)

initial_env = Environment(4, 4, 0, False)
initial_percept = initial_env.get_percepts(skip_reward=True)
log("Start a new world!")
log(initial_env)
log(initial_percept)
agent = BeelineAgent()

total_reward = run_episode(initial_env, agent, initial_percept)
log(f"Total reward: {total_reward}")
