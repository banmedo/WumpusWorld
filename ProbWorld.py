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


# I ran it for 1000 runs and the average was 996.976. Kept it low for the repo since that gives room for quick testing
net_rewards = 0
total_runs = 10
for i in range(0,total_runs):
    log(f"==========================================")
    log(f"     RUN {i+1} starts here!")
    log(f"==========================================")
    # env = Environment(4, 4, 0.2, True, pit_locations=[[0,3],[1,1],[3,2]], wumpus_location=[2,1], gold_location=[2,1])
    env = Environment(4, 4, 0.2, True)
    initial_percept = env.get_percepts(skip_reward=True)
    log("Start a new world!")
    log(env)
    log(initial_percept)
    agent = ProbAgent(env)

    total_reward = run_episode(env, agent, initial_percept)
    log(f"Total reward: {total_reward}")
    net_rewards = net_rewards+total_reward

average_reward = net_rewards / total_runs
print(f"Average reward is {average_reward} after {total_runs} runs")
