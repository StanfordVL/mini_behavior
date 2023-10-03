import numpy as np
import os
import pickle as pkl


def load_demo(filepath):
    with open(filepath, 'rb') as f:
        demo = pkl.load(f)
        # demo = [demo[i] for i in range(len(demo))]
        demo = list(demo.values())
        return demo

def load_demos(demo_dir, num_demos=None):
    demo_filenames = list(os.listdir(demo_dir))
    demos = []
    if num_demos is not None:
        demo_filenames = demo_filenames[: num_demos]
    print(len(demo_filenames))
    for demo_filename in demo_filenames:
        demo_path = os.path.join(demo_dir, demo_filename)
        demo = load_demo(demo_path)
        demos += demo
    return demos


def get_nav_action(init_x, init_y, init_dir, front_is_empty, target_x, target_y, target_dir):
    # get action
    possible_actions = set()
    action_name = None

    if init_x == target_x and init_y == target_y:
        if 0 < (init_dir - target_dir) % 4 <= 2:
            possible_actions.add('left')
        if (init_dir - target_dir) % 4 >= 2:
            possible_actions.add('right')
    else:
        if not front_is_empty:
            possible_actions = {'left', 'right'}
        else:
            if init_x < target_x:
                if init_dir == 0:
                    action_name = 'forward'
                else:
                    if 0 < (init_dir - 0) % 4 <= 2:
                        possible_actions.add('left')
                    if (init_dir - 0) % 4 >= 2:
                        possible_actions.add('right')
            if target_y > init_y:
                if init_dir == 1:
                    action_name = 'forward'
                else:
                    if 0 < (init_dir - 1) % 4 <= 2:
                        possible_actions.add('left')
                    if (init_dir - 1) % 4 >= 2:
                        possible_actions.add('right')
            if target_x < init_x:
                if init_dir == 2:
                    action_name = 'forward'
                else:
                    if 0 < (init_dir - 2) % 4 <= 2:
                        possible_actions.add('left')
                    if (init_dir - 2) % 4 >= 2:
                        possible_actions.add('right')
            if init_y > target_y:
                if init_dir == 3:
                    action_name = 'forward'
                else:
                    if 0 < (init_dir - 3) % 4 <= 2:
                        possible_actions.add('left')
                    if (init_dir - 3) % 4 >= 2:
                        possible_actions.add('right')

    action_name = np.random.choice(list(possible_actions), 1)[0] if action_name is None else action_name

    return action_name


demo_dir = './demos/MiniGrid-InstallingAPrinter-8x8-N2-v0/'
demos = load_demos(demo_dir)
print("successfully loaded demos")
print(f"demos length: {len(demos)}")

