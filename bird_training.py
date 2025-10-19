from bird_game import Birdgame
from flap_model import model, compute_discounted_rewards, action, optimization
import random
from time import sleep
import torch

env = Birdgame(render = True)
num_episodes = 5000
epsilon = 0.30  # exploration probability

for episode in range(num_episodes):
    rewards = []
    total_log_probability = []
    state = env.get_state()
    game_active = True
    print(f'Trial {episode+1}')
    if (episode+1)/1000 == 1:
        torch.save(model.state_dict(), "flap_model.pth")
    while game_active == True:
        act, log_prob = action(state, epsilon)
        next_state, reward, game_act = env.step(act)
        if act == 1:
            print("Jumped")
        else:
            print("Not jumped")
        print(reward)
        rewards.append(reward)
        total_log_probability.append(log_prob)
        # store transition for training
        state = next_state
        if game_act == False:
        # After episode is done, calculate discounted reward and optimize model
            discounted_rewards = compute_discounted_rewards(rewards, gamma=0.99)
            optimization(discounted_rewards, total_log_probability)
            epsilon = epsilon * 0.95
            print(f'You survived for {len(rewards)} frames')
            print(f"Your total reward is {sum(rewards)}")
            env.reset_game()
            break
        else:
            continue
    
    
# model.load_state_dict(torch.load("flap_model.pth"))
# other_env = Birdgame(render = True)





