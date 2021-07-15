import torch
import numpy as np

from src.agent.dql import DQLAgent
from src.world.environment import Environment
from src.world.agent_state import AgentState

from utils import log


def test_model(model, env, agent, max_moves=100):
    percepts = env.get_percepts(skip_reward=True)
    log("Start a new world!")
    log(env)
    log(percepts)
    # get the state of the agent to feed into network
    state = agent.get_agent_state()
    # mutate the state randomly
    state_w_rand = state + (np.random.rand(*state.shape) / 100.0)
    # convert the mutated state to a tensor
    state_tensor = torch.from_numpy(state_w_rand).float()

    # run the game
    num_moves = 0
    total_reward = 0
    while True:
        qval = model(state_tensor)
        qval_arr = qval.data.numpy()
        action_ind = np.argmax(qval_arr)
        action = agent.ACTIONS[action_ind]
        percepts = env.act(action)
        state = agent.act(action, percepts)
        state_w_rand = state + (np.random.rand(*state.shape) / 100.0)
        state_tensor = torch.from_numpy(state_w_rand).float()
        total_reward = total_reward + percepts.reward
        num_moves = num_moves + 1
        log(f"Action : {action}")
        log(env)
        log(percepts)
        log("------------------------------------------")
        if percepts.reward > 0:
            return {"won": True, "score": total_reward}
        elif percepts.is_terminated:
            return {"won": False, "score": total_reward}
        elif num_moves >= max_moves:
            return {"won": False, "score": total_reward}


if __name__ == "__main__":
    model_name = "wumpus_72_512_128_128_128_6"
    # parse nodes from model name
    nodes = [int(n) for n in model_name.split("_")[1:]]
    # build model
    layers = [torch.nn.Linear(nodes[0], nodes[1])]
    for i in range(1, len(nodes)-1):
        layers.append(torch.nn.ReLU())
        layers.append(torch.nn.Linear(nodes[i], nodes[i+1]))
    model = torch.nn.Sequential(*layers)
    # load weights from the file
    model.load_state_dict(torch.load(f"dqlmodel/{model_name}"))

    TEST_NUMB = 10
    won = 0
    total_score = 0
    for i in range(TEST_NUMB):
        # start a new environment
        env = Environment(4, 4, 0.2, True)
        # initialize the agent
        agent = DQLAgent(env)
        result = test_model(model, env, agent)
        if result['won']:
            won = won + 1
        total_score = total_score + result['score']
    print(f"Won {won} games!")
    print("Win ratio is {}".format(won/TEST_NUMB))
    print("Average score is {}".format(total_score/TEST_NUMB))
