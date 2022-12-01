#!/usr/bin/env python3
import argparse
from mini_behavior.window import InteractiveWindow
from bddl.actions import ACTION_FUNC_MAPPING
import mini_behavior.envs # type: ignore
from minigrid.wrappers import ImgObsWrapper, RGBImgPartialObsWrapper
import gymnasium as gym


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
    allowable_actions = {}
    for action_str, action in ACTION_FUNC_MAPPING.items():
        for obj in env.obj_instances.values():
            if action(env).can(obj):
                allowable_actions[f"{action_str} + {obj.name}"] = (action, obj)

    print("Choose an action:")
    for idx, action_str in enumerate(allowable_actions):
        print(f"\t{idx} {action_str}")
    action_idx = None
    while action_idx not in range(len(allowable_actions)):
        candidate_idx = input("Choice: ")
        if candidate_idx in map(str, range(20)):
            action_idx = int(candidate_idx)

    action = list(allowable_actions.values())[action_idx]

    obs, reward, terminated, truncated, info = window.step(action)
    if terminated or truncated:
        print("Episode completed")
