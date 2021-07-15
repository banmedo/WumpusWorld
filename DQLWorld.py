import torch
import random
import copy
import numpy as np
import matplotlib.pyplot as plt

from collections import deque

from utils import log

from src.agent.dql import DQLAgent
from src.world.environment import Environment

nodes = [ 72, 512, 128, 128, 6]

layers = [torch.nn.Linear(nodes[0], nodes[1])]

for i in range(1, len(nodes)-1):
    layers.append(torch.nn.ReLU())
    layers.append(torch.nn.Linear(nodes[i], nodes[i+1]))

model = torch.nn.Sequential(*layers)

model2 = copy.deepcopy(model)
model2.load_state_dict(model.state_dict())

# constants
LEARNING_RATE = 1e-3
GAMMA = 0.9
EPSILON = 0.3
EPOCHS = 3000
MEM_SIZE = 1500
BATCH_SIZE = 100
ACTION_DEPTH = 50
SYNC_FREQ = 500

loss_fn = torch.nn.MSELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=LEARNING_RATE)
replay = deque(maxlen=MEM_SIZE)
losses = []

sync_step = 0

# start an epoch
for i in range(EPOCHS):
    # start a new environment
    env = Environment(4, 4, 0.2, False)
    # initialize the agent
    agent = DQLAgent(env)
    # get the state of the agent to feed into network
    state = agent.get_agent_state() 
    # mutate the state randomly
    state_w_rand = state + (np.random.rand(1, 72) / 100.0)
    # convert the mutated state to a tensor
    state_tensor = torch.from_numpy(state_w_rand).float()
    # counter for the number of actions that can be taken
    n_actions = 0
    # get cumulative game reward
    game_reward = 0
    # a memory for states to track if we've been in the state before
    episode_memory = deque()
    episode_memory.append(state_tensor)
    while n_actions < ACTION_DEPTH:
        # increase the sync_step and number of actions taken
        sync_step = sync_step + 1
        n_actions = n_actions + 1
        # run the model and get qvalues
        qval = model(state_tensor)
        qval_arr = qval.data.numpy()
        # randomly select a random action based on epsilon
        if random.random() < EPSILON:
            action_ind = np.random.randint(0,len(agent.ACTIONS))
        else:
            action_ind = np.argmax(qval_arr)
        action = agent.ACTIONS[action_ind]
        # act on the env and get percepts from env
        percepts = env.act(action)
        log(percepts)
        log(env)
        # the agent performs the action so update the agent object
        # and returns the new state
        new_state = agent.act(action, percepts)
        # mutation and conversion to tensor
        new_state_w_rand = new_state + (np.random.rand(1, 72) / 100.0)
        new_state_tensor = torch.from_numpy(new_state_w_rand).float()
        # add action reward to game reward
        game_reward = game_reward + percepts.reward
        # log experience
        experience = (
            state_tensor, 
            action_ind, 
            # game_reward, # total reward?
            percepts.reward, 
            new_state_tensor, 
            percepts.is_terminated
        )

        # if the new state is a recognized state
        if len([exp[0] for exp in episode_memory if torch.equal(new_state_tensor, exp[0])]) > 0:
            percepts.reward = -1001
            percepts.is_terminated = True
        else:
            episode_memory.append(new_state_tensor)

        # add experience to replay
        replay.append(experience)
        # update state variable for new run 
        state = new_state

        # once we have enough states
        if len(replay) > BATCH_SIZE:
            minibatch = random.sample(replay, BATCH_SIZE)
            state_batch = torch.cat([experience[0] for experience in minibatch])
            action_batch = torch.Tensor([experience[1] for experience in minibatch])
            reward_batch = torch.Tensor([experience[2] for experience in minibatch])
            new_state_batch = torch.cat([experience[3] for experience in minibatch])
            done_batch = torch.Tensor([experience[4] for experience in minibatch])
            Q1 = model(state_batch)
            with torch.no_grad():
                Q2 = model2(new_state_batch)
            
            y = reward_batch + GAMMA * ((1 - done_batch) * torch.max(Q2, dim = 1)[0])
            x = Q1.gather(
                    dim = 1,
                    index = action_batch.long().unsqueeze(dim = 1)
                ).squeeze()
            loss = loss_fn(x, y.detach())
            optimizer.zero_grad()
            loss.backward()
            losses.append(loss.item())
            optimizer.step()

            if sync_step % SYNC_FREQ == 0:
                print("On a sync step!")
                model2.load_state_dict(model.state_dict())
        if percepts.is_terminated:
            break

losses = np.array(losses)
# print(losses)

file_suffix = "_".join([str(n) for n in nodes])

plt.figure(figsize = (10,7))
plt.plot(losses)
plt.xlabel("Epochs", fontsize=22)
plt.ylabel("Loss", fontsize=22)
plt.savefig(f"graphs/loss_{file_suffix}.png")

torch.save(model.state_dict(), f"dqlmodel/wumpus_{file_suffix}")
