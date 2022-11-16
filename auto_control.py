import gymnasium as gym
# from minigrid.wrappers import RGBImgPartialObsWrapper, ImgObsWrapper
from mini_behavior.window import Window
from lm import SayCanOPT as SayCan
import numpy as np


env_id = 'MiniGrid-InstallingAPrinter-16x16-N2-v1'
env = gym.make(env_id)
saycan = SayCan(task=env.mission)

all_steps = {}

# if args.agent_view:
#     env = RGBImgPartialObsWrapper(env)
#     env = ImgObsWrapper(env)

window = Window('mini_behavior - ' + env_id)

rng = np.random.default_rng()
seed = rng.integers(int(1e6))
env.reset(seed=seed, options={})

for _ in range(5):
    affordances, affordance_labels = env.affordances()
    action = saycan.get_action(affordances, affordance_labels)

    obs, reward, terminated, truncated, info = env.step(action)

    print('step=%s, reward=%.2f' % (env.step_count, reward))

    # if args.save:
    #     step_count, step = get_step(env)
    #     all_steps[step_count] = step

    if terminated or truncated:
        print('done!')
        # if args.save:
        #     save_demo(all_steps, args.env, env.episode)

        seed = rng.integers(int(1e6))
        env.reset(seed=seed, options={})
    # else:
    #     redraw(obs)


