import argparse

import gym
import numpy
import random
import mini_behavior
import torch
from stable_baselines3 import PPO

# For RL visualization
from gym_minigrid.wrappers import ImgObsWrapper
from mini_behavior.utils.wrappers import MiniBHFullyObsWrapper
from mini_behavior.register import register

# Parse arguments
parser = argparse.ArgumentParser()
parser.add_argument("--env",
                    default="InstallingAPrinter",
                    help="name of the environment to be run (REQUIRED)")
parser.add_argument("--room_size", type=int, default=10)
parser.add_argument("--max_steps", type=int, default=1000)
parser.add_argument("--dense_reward", action="store_true")
parser.add_argument("--seed", type=int, default=20,
                    help="random seed (default: 0)")
parser.add_argument("--shift", type=int, default=0,
                    help="number of times the environment is reset at the beginning (default: 0)")
parser.add_argument("--pause", type=float, default=0.25,
                    help="pause duration between two consequent actions of the agent (default: 0.seed 0_2)")
parser.add_argument("--gif", type=str, default=None,
                    help="store output as gif with the given filename")
parser.add_argument("--episodes", type=int, default=1000000,
                    help="number of episodes to visualize")
parser.add_argument("--reset", action="store_true", default=False,
                    help="Keep resetting for testing initialization")
parser.add_argument("--norend", action="store_true", default=False,
                    help="Whether to render")
parser.add_argument("--full_obs", action="store_true", default=False,
                    help="Whether to use fully observable wrapper")
parser.add_argument("--load_model", default="",
                    help="Whether to load from")

args = parser.parse_args()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

def seed(seed):
    random.seed(seed)
    numpy.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)

# Set seed for all randomness sources
seed(args.seed)

# Set device
print(f"Device: {device}\n")


# Env wrapping
env_name = f"MiniGrid-{args.env}-{args.room_size}x{args.room_size}-N2-v0"

print(f'register env {args.env}')

kwargs = {"room_size": args.room_size, "max_steps": args.max_steps}
if args.dense_reward:
    assert args.env in ["PuttingAwayDishesAfterCleaning", "WashingPotsAndPans"]
    kwargs["dense_reward"] = True

register(
    id=env_name,
    entry_point=f'mini_behavior.envs:{args.env}Env',
    kwargs=kwargs
)

# Load environment
env = gym.make(env_name)
if args.full_obs:
    env = MiniBHFullyObsWrapper(env)
env = ImgObsWrapper(env)
env.seed(args.seed)

for _ in range(args.shift):
    env.reset()
print("Environment loaded\n")

load_model = args.load_model

if load_model:
    # Load Model
    model = PPO.load(f"model/{load_model}", env=env)
    print("model loaded")


if args.gif:
   from array2gif import write_gif
   frames = []

if not args.norend:
    # Create a window to view the environment
    env.render('human')

for episode in range(args.episodes):
    obs = env.reset()

    # To test reset
    if args.reset:
        while True:
            env.render('human')
            obs = env.reset()

    while True:
        if not args.norend:
            env.render('human')
        if args.gif:
            frames.append(numpy.moveaxis(env.render("rgb_array"), 2, 0))

        
        if load_model:
            action, _ = model.predict(obs)
        else:
            action = env.action_space.sample()

        obs, reward, done, info = env.step(action)

        if env.mode == "cartesian":
            print(env.action_list[action])
        else:
            print(env.actions(action).name)

        print(f"reward: {reward}\n")

        if done:
            print("episode done")
            print(f"reward: {reward}")
            break
        # import sys
        # import numpy as np
        # np.set_printoptions(threshold=sys.maxsize)
        # print(obs)
        # import ipdb
        # ipdb.set_trace()

    print("one episode done \n")

if args.gif:
    print("Saving gif... ", end="")
    write_gif(numpy.array(frames), args.gif+".gif", fps=1/args.pause)
    print("Done.")
