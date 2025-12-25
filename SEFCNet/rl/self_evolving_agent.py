import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim


# Simple reinforcement learning agent to evolve client behavior dynamically
class SelfEvolvingAgent:
def __init__(self, state_dim=3, action_dim=3, lr=0.001, gamma=0.9):
self.gamma = gamma
self.model = nn.Sequential(
nn.Linear(state_dim, 32),
nn.ReLU(),
nn.Linear(32, action_dim),
nn.Softmax(dim=-1)
)
self.optimizer = optim.Adam(self.model.parameters(), lr=lr)
self.loss_fn = nn.MSELoss()


def select_action(self, state):
state_tensor = torch.tensor(state, dtype=torch.float32)
probs = self.model(state_tensor)
action = torch.argmax(probs).item()
return action


def train(self, state, reward, next_state):
state_tensor = torch.tensor(state, dtype=torch.float32)
next_state_tensor = torch.tensor(next_state, dtype=torch.float32)
reward_tensor = torch.tensor(reward, dtype=torch.float32)


# Compute targets using basic Bellman equation
current_value = torch.max(self.model(state_tensor))
next_value = torch.max(self.model(next_state_tensor))
target = reward_tensor + self.gamma * next_value


loss = self.loss_fn(current_value, target.detach())
self.optimizer.zero_grad()
loss.backward()
self.optimizer.step()
return loss.item()