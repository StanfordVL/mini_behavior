# FROM RL TORCH

import gymnasium as gym
import minigrid


def make_env(env_key, seed=None):
    env = gym.make(env_key)
    env.seed(seed)
    return env
