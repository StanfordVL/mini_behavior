#!/usr/bin/env python3
import argparse
from mini_behavior.window import InteractiveWindow
from bddl.actions import get_allowable_actions
import mini_behavior.envs # type: ignore
from minigrid.wrappers import ImgObsWrapper, RGBImgPartialObsWrapper
import gymnasium as gym

assert mini_behavior.envs is not None

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--env",
        help="gym environment to load",
        default="MiniGrid-InstallingAPrinter-16x16-N2-v1",
    )
    parser.add_argument(
        "--seed",
        type=int,
        help="random seed to generate the environment with",
        default=-1,
    )
    parser.add_argument(
        "--tile_size", type=int, help="size at which to render tiles", default=32
    )
    parser.add_argument(
        "--agent_view",
        default=False,
        help="draw the agent sees (partially observable view)",
        action="store_true",
    )
    # NEW
    parser.add_argument(
        "--save", default=False, help="whether or not to save the demo_16"
    )
    # NEW
    parser.add_argument("--load", default=None, help="path to load state from")

    args = parser.parse_args()
    return args

from mini_behavior.planning.tasks import solve_boxing, solve_printer

if __name__ == "__main__":
    args = get_args()
    env = gym.make(args.env)
    window = InteractiveWindow(env)

    if args.agent_view:
        env = RGBImgPartialObsWrapper(env)
        env = ImgObsWrapper(env)

    if args.load is None:
        window.reset()
    else:
        window.load()

    while True:
        while True:
            action_strs, actions = get_allowable_actions(env)
            action_idx = window.user_control(action_strs)
            action = actions[action_idx]
            obs, reward, terminated, truncated, info = window.step(action)
            # terminated = False
            # truncated = True
            # for action in solve_printer(env):
            #     obs, reward, terminated, truncated, info = window.step(action)

            if terminated or truncated:
                break
