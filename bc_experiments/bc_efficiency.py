# FROM RL TORCH

from bc_agent import Agent
from mini_behavior.envs.bc_installing_a_printer import *
from gym_minigrid.wrappers import *
import os
import argparse
from mini_behavior.demo_utils import load_demo

parser = argparse.ArgumentParser()
parser.add_argument(
    "--model_path",
    help="filename of model"
)
parser.add_argument(
    "--env_name",
)
parser.add_argument(
    "--demo_dir",
)

args = parser.parse_args()

# initialize env
env_name = args.env_name
demo_dir = args.demo_dir
env = gym.make(env_name)
env.seed(1337)

print("Environment loaded\n")

env.render('human')
print("Window loaded\n")

model_path = args.model_path

efficiencies = []

demo_filenames = list(os.listdir(demo_dir))
for i in range(100):
    demo_path = os.path.join(demo_dir, demo_filenames[i])
    demo = load_demo(demo_path)

    state_0 = demo[0][0]
    # Load agent
    agent = Agent(env.observation_space, env.action_space, model_path)
    # Run agent
    obs = env.reset()
    env.agent_pos = (state_0['agent_x'], state_0['agent_y'])
    env.agent_dir = int(state_0['agent_dir'])

    while True:
        env.render('human')

        action = agent.get_action(obs)
        obs, reward, done, _ = env.step(action)

        if done:
            efficiency = env.step_count / len(demo)
            efficiencies.append(efficiency)
            break

        if env.step_count >= env.max_steps:
            break

    if i % 10 == 0:
        print(np.mean(efficiencies))

print(efficiencies)
print('avg efficiency')
print(np.mean(efficiencies))
