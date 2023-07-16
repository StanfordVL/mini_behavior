import os
import pickle as pkl


def all_cur_pos(env):
    """
    returns dict with key=obj, value=cur_pos
    """
    pos = {'agent': [int(obj_pos) for obj_pos in env.agent.cur_pos]}

    for obj_name in env.obj_instances:
        obj_instance = env.obj_instances[obj_name]
        pos[obj_name] = [int(obj_pos) for obj_pos in obj_instance.cur_pos]

    return pos


def all_state_values(env):
    """
    returns dict with key=obj_state, value=state value
    """
    states = {}
    for obj_name, obj_instance in env.obj_instances.items():
        obj_states = obj_instance.get_all_state_values(env)
        states.update(obj_states)
    return states


# save last action, all states, all obj pos, all door pos
def get_step(env):
    step_count = env.step_count
    action = 'none' if env.last_action is None else env.last_action.name
    state = env.get_state()
    state_values = all_state_values(env)

    # door_pos = []
    # for door in env.doors:
    #     door_pos.append(door.cur_pos)
    step = {'action': action,
            'predicates': state_values,
            'grid': state['grid'],
            'agent_dir': state['agent']['dir'],
            'agent_pos': state['agent']['cur_pos']
            # 'door_pos': door_pos
            }

    return step_count, step


# save demo_16 as a pkl file
def save_demo(all_steps, env_name, episode):
    demo_dir = os.path.join('./demos', env_name)
    if not os.path.isdir(demo_dir):
        os.makedirs(demo_dir)
    all_files = os.listdir(demo_dir)
    demo_num = len(all_files)
    demo_file = os.path.join(demo_dir, '{}_{}'.format(env_name, demo_num))
    assert not os.path.isfile(demo_file)

    print('saving demo to: {}'.format(demo_file))

    with open(demo_file, 'wb') as f:
        pkl.dump(all_steps, f)

    print('saved')


# save demo_16 as a pkl file
def save_snapshots(env_steps, model_name='', date=''):
    dir = '../snapshots'
    if not os.path.isdir(dir):
        os.mkdir(dir)
    snapshot_file = os.path.join(dir, f'{model_name}_{date}')

    print('saving snapshot to: {}'.format(snapshot_file))

    # hf = h5py.File('{demo_file}.h5', 'w')

    with open(snapshot_file, 'wb') as f:
        pkl.dump(env_steps, f)

    print('saved')


def open_demo(demo_file):
    assert os.path.isfile(demo_file)

    with open(demo_file, 'rb') as f:
        demo = pkl.load(f)
        print('num_steps in demo_16: {}'.format(len(demo)))
        return demo


def get_step_num(step_num, demo_file):
    # returns dict with keys: action, grid, agent_carrying, agent_pos
    demo = open_demo(demo_file)
    return demo[step_num]


def get_action_num(step_num, demo_file):
    demo = open_demo(demo_file)
    action = demo[step_num]['action']
    print('action at step {}: {}'.format(step_num, action.name))
    return action


def get_states(step_num, demo_file):
    demo = open_demo(demo_file)
    states = demo[step_num]['states']
    return states


def print_actions_states(demo_file):
    demo = open_demo(demo_file)
    for step_num in demo:
        print('{}: {}'.format(step_num,  demo[step_num]['action']))
        print('true predicates')
        for state in demo[step_num]['predicates']:
            if demo[step_num]['predicates'][state]:
                print(state)


def print_actions(demo_file):
    demo = open_demo(demo_file)
    for step_num in demo:
        print('{}: {}'.format(step_num,  demo[step_num]['action']))


# demo_file = '/Users/emilyjin/Code/behavior/demos/MiniGrid-ThrowLeftoversFourRooms-8x8-N2-v1/2/MiniGrid-ThrowLeftoversFourRooms-8x8-N2-v1_10'
# print_actions_states(demo_file)
