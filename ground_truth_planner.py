import gymnasium as gym
from mini_behavior.window import Window
import numpy as np
import gc
# from memory_profiler import profile


env_id = 'MiniGrid-InstallingAPrinter-16x16-N2-v1'
# env_id = 'MiniGrid-CollectMisplacedItems-16x16-N2-v1'
# env_id = 'MiniGrid-ThrowingAwayLeftovers-16x16-N2-v1'
env = gym.make(env_id)

all_steps = {}

rng = np.random.default_rng()
seed = rng.integers(int(1e6))
env.reset(seed=seed, options={})

# BFS algorithm to find the shortest action sequence to complete the task
# @profile
def get_ground_truth_plan(env, max_depth=100):
    init_state = env.get_state()
    init_action_history = []
    queue = []
    queue.append((init_state, init_action_history))
    while queue:
        curr_state, curr_action_history = queue.pop(0)
        if len(curr_action_history) >= max_depth:
            return None
        # env.reset(seed=seed, options={})
        env.load_state(curr_state)
        affordances, affordance_labels = env.affordances()
        for action, action_human_readable in zip(affordances, affordance_labels):
            env.load_state(curr_state)
            obs, reward, terminated, truncated, info = env.step(action)
            if env.action_done:
                next_state = env.get_state()
                next_action_history = curr_action_history + [action_human_readable]
                print(next_action_history)
                if terminated:
                    print('done!')
                    return next_action_history
                queue.append((next_state, next_action_history))
        curr_state['grid'] = None
        curr_state['objs'] = None
        curr_action_history = None
        # env = gym.make(env_id)
        env.reset(seed=seed, options={})
        print(len(queue), gc.collect())
    return None

def get_ground_truth_plan_randomly_sampled(env, max_depth=200, num_samples=200):
    init_state = env.get_state()
    shortest_action_sequence = None
    for i in range(num_samples):
        env.load_state(init_state)
        action_history = []
        for j in range(max_depth):
            affordances, affordance_labels = env.affordances()
            action = tuple(rng.choice(affordances))
            action_human_readable = affordance_labels[affordances.index(action)]
            obs, reward, terminated, truncated, info = env.step(action)
            if env.action_done:
                action_history.append(action_human_readable)
                if terminated:
                    # print('done!')
                    if shortest_action_sequence is None or len(action_history) < len(shortest_action_sequence):
                        shortest_action_sequence = action_history
                    break
        # print(i, action_history)
        print(i, len(shortest_action_sequence) if shortest_action_sequence else -1)
    return shortest_action_sequence

print(get_ground_truth_plan_randomly_sampled(env))