import gym
from gym import spaces
from mini_bddl import OBJECT_TO_IDX


class MiniBHFullyObsWrapper(gym.core.ObservationWrapper):
	"""
	Fully observable gridworld using a compact grid encoding
	MiniBH encoding is different from MiniGrid encoding
	"""

	def __init__(self, env):
		super().__init__(env)

		self.unwrapped.use_full_obs = True
		self.observation_space.spaces["image"] = spaces.Box(
			low=0,
			high=255,
			shape=(self.env.width, self.env.height, env.grid.pixel_dim),  # number of cells
			dtype='uint8'
		)

	def observation(self, obs):
		return obs
