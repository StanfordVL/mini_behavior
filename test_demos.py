# FROM RL TORCH

from gym_minigrid.wrappers import *
import os
import argparse
from installing_a_printer.utils import load_demo

ALL_DEMOS_DIR = '/Users/emilyjin/Code/behavior/mini_behavior/demos'

parser = argparse.ArgumentParser()
parser.add_argument(
    "--task",
    help="task to complete",
    default='SimpleInstallingAPrinter'
)
parser.add_argument(
    "--room_size",
    help="room size",
    default=8
)
parser.add_argument(
    "--tile_size",
    type=int,
    help="size at which to render tiles",
    default=32
)

args = parser.parse_args()

# initialize env
env_name = f'MiniGrid-{args.task}-{args.room_size}x{args.room_size}-N2-v0'
env = gym.make(env_name)
# env.seed(args.seed)

print("Environment loaded\n")

env.render('human')
print("Window loaded\n")

demo_dir = os.path.join(ALL_DEMOS_DIR, args.task, str(args.room_size))
assert os.path.isdir(demo_dir)
demo_filenames = os.listdir(demo_dir)

for demo_filename in demo_filenames:
    demo_json = {}
    env.reset()

    demo_path = os.path.join(demo_dir, demo_filename)
    demo = load_demo(demo_path)

    state_0, _ = demo[0]

    demo_json['init_x'] = int(state_0['agent_x'])
    demo_json['init_y'] = int(state_0['agent_y'])
    demo_json['init_dir'] = int(state_0['agent_dir'])

    print(state_0)
    env.agent_pos = (state_0['agent_x'], state_0['agent_y'])
    env.agent_dir = state_0['agent_dir']
    # env.render('human')

    for step in demo:
        # next = input('press space to do next action')
        action = step[1]
        print(action.name)
        actions_so_far = demo_json.get('actions', [])
        actions_so_far.append(action.name)
        demo_json['actions'] = actions_so_far
        obs, reward, done, _ = env.step(action)
        # env.render('human')

    # out_file = os.path.join('/Users/emilyjin/Code/behavior/mini_behavior/demo_json', f'{demo_filename}.json')
    # with open(out_file, 'w') as f:
    #     json.dump(demo_json, f)

    # break
    # if not done:
    #     print(f'unsuccessful demo {demo_filename}')
