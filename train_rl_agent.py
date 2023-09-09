import gym
from gym_minigrid.wrappers import ImgObsWrapper
import mini_behavior
from stable_baselines3 import PPO
from gym import spaces
import numpy as np
from mini_bddl import OBJECT_TO_IDX


class MiniBHFullyObsWrapper(gym.core.ObservationWrapper):
	"""
	Fully observable gridworld using a compact grid encoding
	MiniBH encoding is different from MiniGrid encoding
	"""

	def __init__(self, env):
		super().__init__(env)

		self.observation_space.spaces["image"] = spaces.Box(
			low=0,
			high=255,
			shape=(self.env.width, self.env.height, env.grid.pixel_dim),  # number of cells
			dtype='uint8'
		)

	def observation(self, obs):
		env = self.unwrapped
		full_grid = env.grid.encode()
		# Set the agent state and direction as part of the observation
		full_grid[env.agent_pos[0]][env.agent_pos[1]][0] = OBJECT_TO_IDX['agent']
		full_grid[env.agent_pos[0]][env.agent_pos[1]][1] = env.agent_dir

		return {
			'mission': obs['mission'],
			'image': full_grid
		}

# Env wrapping
env = gym.make("MiniGrid-InstallingAPrinter-6x6-N2-v0")
env = MiniBHFullyObsWrapper(env)
env = ImgObsWrapper(env)

# Policy training
model = PPO('MlpPolicy', env, verbose=1, tensorboard_log="./")
model.learn(500)
