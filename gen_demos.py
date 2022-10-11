import gym
import pickle as pkl
import os
import argparse

from mini_behavior.envs.bc_installing_a_printer import *
from gym_minigrid.wrappers import *

from demo_utils import *


ALL_DEMOS_DIR = '/Users/emilyjin/Code/behavior/mini_behavior/demos'


def step(target_x, target_y, target_dir):
    obs = env.gen_obs()

    # get action
    front_is_empty = env.grid.is_empty(*env.front_pos)
    action_name = get_nav_action(*env.agent_pos, env.agent_dir, front_is_empty, target_x, target_y, target_dir)
    action = env.actions[action_name]

    # do action
    env.step(action)

    demo[env.step_count] = (obs, action)
    actions.append(action)


def navigate(obj_x, obj_y):
    target_poss = [(obj_x - 1, obj_y), (obj_x, obj_y - 1), (obj_x + 1, obj_y), (obj_x, obj_y + 1)]

    possible_dirs = set()
    if env.agent_pos[0] < obj_x:
        possible_dirs.add(0)
    if obj_y > env.agent_pos[1]:
        possible_dirs.add(1)
    if obj_x < env.agent_pos[0]:
        possible_dirs.add(2)
    if env.agent_pos[1] > obj_y:
        possible_dirs.add(3)

    target_dir = np.random.choice(list(possible_dirs), 1)[0]
    target_x, target_y = target_poss[target_dir]

    # num_steps = 0
    while target_x != env.agent_pos[0] or target_y != env.agent_pos[1] or target_dir != env.agent_dir:
        # if num_steps > 200:
        #     return False
        step(target_x, target_y, target_dir)
        # num_steps += 1


def save_actions():
    task_dir = os.path.join(ALL_DEMOS_DIR, args.task)
    if not os.path.isdir(task_dir):
        os.mkdir(task_dir)
    demo_dir = os.path.join(task_dir, str(args.room_size))
    if not os.path.isdir(demo_dir):
        os.mkdir(demo_dir)
    demo_file = f'episode_{env.episode}'
    out_file = os.path.join(demo_dir, demo_file)
    print(out_file)
    with open(out_file, 'wb') as f:
        pkl.dump(demo, f)


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
    "--num_demos",
    help="number of demos",
    default=100
)
parser.add_argument(
   "--env_name",
   default=None
)
args = parser.parse_args()

# initialize env
env_name = args.env_name if args.env_name is not None else f'MiniGrid-{args.task}-{args.room_size}x{args.room_size}-N2-v0'
env = gym.make(env_name)
env.seed(args.seed)

print("Environment loaded\n")

env.render('human')
print("Window loaded\n")

obs = env.reset()
env.render('human')

# get printer pos, table pos
printer_pos = env.printer.cur_pos
table_pos = (27, 30)

num_demos = 0
for i in range(int(args.num_demos)):
    print(i)
# while num_demos < int(args.num_demos):
    demo = {}
    actions = []

    env.reset()
    env.render('human')

    # navigate to printer
    navigate(*printer_pos)

    # pickup printer
    assert(env.printer.check_abs_state(env, 'inreachofrobot'))
    obs = env.gen_obs()
    env.step(env.actions.pickup)
    demo[env.step_count] = (obs, env.actions.pickup)
    actions.append(env.actions.pickup)

    assert(env.printer.check_abs_state(env, 'inhandofrobot'))

    # navigate to table
    navigate(*table_pos)

    # drop printer
    assert(env.printer.check_abs_state(env, 'inreachofrobot'))
    assert(env.table.check_abs_state(env, 'inreachofrobot'))
    obs = env.gen_obs()
    env.step(env.actions.drop)
    demo[env.step_count] = (obs, env.actions.drop)
    actions.append(env.actions.drop)
    assert not env.printer.check_abs_state(env, 'inhandofrobot')
    assert env.printer.check_rel_state(env, env.table, 'onTop')

    # toggle printer
    assert(env.printer.check_abs_state(env, 'inreachofrobot'))
    obs = env.gen_obs()
    env.step(env.actions.toggle)
    demo[env.step_count] = (obs, env.actions.toggle)
    actions.append(env.actions.toggle)

    # check that sequence is successful
    assert env.printer.check_rel_state(env, env.table, 'onTop') and env.printer.check_abs_state(env, 'toggleable')

    # save actions
    save_actions()


