from src.agent.prob import ProbAgent

from src.world.environment import Environment

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

env = Environment(4, 4, 0.2, True)
initial_percept = env.get_percepts(skip_reward=True)
log("Start a new world!")
log(env)
log(initial_percept)
agent = ProbAgent(env)

total_reward = run_episode(env, agent, initial_percept)
log(f"Total reward: {total_reward}")
