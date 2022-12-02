import gymnasium as gym
from mini_behavior.window import Window
import numpy as np


env_id = 'MiniGrid-InstallingAPrinter-16x16-N2-v1'
env = gym.make(env_id)

all_steps = {}

rng = np.random.default_rng()
seed = rng.integers(int(1e6))
env.reset(seed=seed, options={})

# BFS algorithm to find the shortest action sequence to complete the task
def get_ground_truth_plan(env):
    init_state = env.get_state()
    init_action_history = []
    queue = []
    queue.append((init_state, init_action_history))
    while queue:
        curr_state, curr_action_history = queue.pop(0)
        # env.reset(seed=seed, options={})
        env.load_state(curr_state)
        affordances, affordance_labels = env.affordances()
        for action, action_human_readable in zip(affordances, affordance_labels):
            env.load_state(curr_state)
            obs, reward, terminated, truncated, info = env.step(action)
            if env.action_done:
                next_state = env.get_state()
                next_action_history = curr_action_history + [action_human_readable]
                if terminated:
                    print('done!')
                    return next_action_history
                queue.append((next_state, next_action_history))
    return None

print(get_ground_truth_plan(env))