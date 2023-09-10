import gym
from gym_minigrid.wrappers import ImgObsWrapper
from mini_behavior.utils.wrappers import MiniBHFullyObsWrapper
import mini_behavior
from stable_baselines3 import PPO
import numpy as np
from stable_baselines3.common.env_util import make_vec_env

# Env wrapping
env = gym.make("MiniGrid-InstallingAPrinter-6x6-N2-v0")
env = MiniBHFullyObsWrapper(env)
env = ImgObsWrapper(env)

# Policy training
model = PPO('MlpPolicy', env, verbose=1, tensorboard_log="./logs/")
model.learn(1000000)

model.save("model/ppo")
