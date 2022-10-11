# FROM RL TORCH

import time
from bc_experiments.bc_agent import Agent
from mini_behavior.envs.bc_installing_a_printer import *
from gym_minigrid.wrappers import *
import os
import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    "--task",
    help="task to complete",
    default='SimpleInstallingAPrinter'
)
parser.add_argument(
    "--room_size",
    help="size of room",
    default=8
)
parser.add_argument(
    "--seed",
    type=int,
    help="random seed to generate the environment with",
    default=1337
)
parser.add_argument(
    "--tile_size",
    type=int,
    help="size at which to render tiles",
    default=32
)
parser.add_argument(
    "--model",
    help="filename of model",
    default=None
)
parser.add_argument(
    "--model_path",
    help="model path",
    default=None
)
parser.add_argument(
    "--num_episodes",
    type=int,
    help="num episodes to test on",
    default=10
)
parser.add_argument(
    "--env_name",
    help="num episodes to test on",
    default=None
)

args = parser.parse_args()

# initialize env
assert args.env_name is not None or (args.task is not None and args.room_size is not None)
env_name = args.env_name if args.env_name is not None else f'MiniGrid-{args.task}-{args.room_size}x{args.room_size}-N2-v0'
env = gym.make(env_name)
env.seed(args.seed)

print("Environment loaded\n")

env.render('human')
print("Window loaded\n")


ALL_MODELS_DIR = '/mini_behavior/models'
model_dir = os.path.join(ALL_MODELS_DIR, args.task, str(args.room_size))

assert args.model_path is not None or args.model is not None, 'no model'
model_path = args.model_path if args.model_path is not None else os.path.join(model_dir, args.model)

successes = []

for i in range(int(args.num_episodes)):
    # Load agent
    agent = Agent(env.observation_space, env.action_space, model_path)

    print("Agent loaded\n")

    # Run agent
    start_time = time.time()
    obs = env.reset()

    while True:
        env.render('human')
        save_dir = os.path.join('grid_screenshots', env_name)
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)
        save_dir = os.path.join(save_dir, f'eps_{env.episode}')
        if not os.path.isdir(save_dir):
            os.mkdir(save_dir)
        out_filepath = os.path.join(save_dir, f'step_{env.step_count}.png')
        env.window.save_img(out_filepath)
        print(f'saved img to {out_filepath}')
        action = agent.get_action(obs)
        obs, reward, done, _ = env.step(action)

        if done:
            successes.append(env.episode)
            break

        if env.step_count >= env.max_steps:
            break

    if i % 10 == 0:
        print(env.episode)
        print(len(successes) / env.episode)

print(successes)
print(env.episode)
