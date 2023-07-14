import gym
from gym_minigrid.wrappers import ImgObsWrapper, FullyObsWrapper
import mini_behavior
from stable_baselines3 import PPO

# Env wrapping
env = gym.make("MiniGrid-InstallingAPrinter-8x8-N2-v0")
env = FullyObsWrapper(env)
env = ImgObsWrapper(env)

# Policy training
model = PPO('MlpPolicy', env, verbose=1, tensorboard_log="./")
model.learn(500)
