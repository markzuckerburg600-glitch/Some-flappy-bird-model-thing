import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.distributions import Categorical
import random

class model (nn.Module):
    def __init__(self):
        super(model, self).__init__()
        self.fc = nn.Sequential(
            nn.Linear(5,128),
            nn.ReLU(),
            nn.Linear(128,2),
            nn.Softmax(dim = 1),
        )
    def forward(self, x):
        return self.fc(x)
    
    def predict_next_action(self, state):
        state = torch.tensor(state, dtype=torch.float32)
        state = state.unsqueeze(0)
        probs = self.forward(state)
        return probs

def compute_discounted_rewards(rewards, gamma=0.99):
    discounted_rewards = []
    R = 0
    for r in reversed(rewards):
        R = r + gamma * R
        discounted_rewards.insert(0, R)
    discounted_rewards = torch.tensor(discounted_rewards)
    discounted_rewards = (discounted_rewards - discounted_rewards.mean()) / (discounted_rewards.std() + 1e-5)
    return discounted_rewards

def action(state, epsilon):
    if np.random.rand() < epsilon:
        action = random.randint(0,1)
        probs = model_instance.predict_next_action(state)
        probs = probs.squeeze(0)
        m = Categorical(probs)
        ye = torch.tensor(action)
        # Finds probability of the random action you chose from the distribution. 
        # Whenever you use log_prob, convert the input into a tensor. If you're sampling, it's already a tensor
        log_prob = m.log_prob(ye)
        return action, log_prob
    else:
        # Get probabilities and create distribution to sample from
        probs = model_instance.predict_next_action(state)
        probs = probs.squeeze(0)
        m = Categorical(probs)
        # Model chooses either 0: no jump or 1: jump. Sample from the distribution
        act = m.sample()
        # Use log_prob function to find log probability of the action from the distribution
        log_prob = m.log_prob(act)
        # Index 1 higher means you jump
        if act.item() == 1:
            return 1, log_prob
        else:
            return 0, log_prob

model_instance = model()
optimizer = torch.optim.Adam(model_instance.parameters(), lr = 1e-3)

def optimization(discounted_rewards, total_log_prob):
    if isinstance(total_log_prob, list):
        total_log_prob = torch.stack(total_log_prob)
    optimizer.zero_grad()
    discounted_rewards = torch.tensor(discounted_rewards,dtype = torch.float32)
    loss = -torch.mean(total_log_prob * discounted_rewards)
    print(float(loss))
    loss.backward()
    optimizer.step()

    
