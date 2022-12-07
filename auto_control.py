import gymnasium as gym
# from minigrid.wrappers import RGBImgPartialObsWrapper, ImgObsWrapper
from mini_behavior.window import Window
from lm import SayCan#OPT as SayCan
import numpy as np


env_id = 'MiniGrid-InstallingAPrinter-16x16-N2-v1'
env = gym.make(env_id)
saycan = SayCan(task=env.mission)

all_steps = {}

rng = np.random.default_rng()
seed = rng.integers(int(1e6))
env.reset(seed=seed, options={})

for _ in range(10):
    affordances, affordance_labels = env.affordances()
    action = saycan.get_action(affordances, affordance_labels)

    obs, reward, terminated, truncated, info = env.step(action)

    print('action:', action)
    print('step=%s, reward=%.2f' % (env.step_count, reward))

    if terminated or truncated:
        print('done!')
        seed = rng.integers(int(1e6))
        env.reset(seed=seed, options={})
