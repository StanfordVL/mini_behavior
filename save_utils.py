import os
import pickle as pkl
import h5py


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
        print(obj_instance.cur_pos)
        print(obj_instance)
        print(env.agent.carrying)
        obj_states = obj_instance.get_all_state_values(env)
        states.update(obj_states)
    return states


def get_grid_agent(env):
    state = env.get_state()
    grid = state['grid']
    agent = state['agent']
    return grid, agent


# save last action, all states, all obj pos, all door pos
def save_step(all_steps, env):
    step_count = env.step_count
    if env.last_action is None:
        action = 'none'
    else:
        action = env.last_action.name
    states = all_state_values(env)
    # pos = all_cur_pos(env)
    grid, agent = get_grid_agent(env)

    # door_pos = []
    # for door in env.doors:
    #     door_pos.append(door.cur_pos)
    all_steps[step_count] = {'action': action,
                             'states': states,
                             # 'pos': pos,
                             'grid': grid,
                             'agent_carrying': agent['carrying'],
                             'agent_pos': agent['cur_pos']
                             # 'door_pos': door_pos
                             }


# save demo as a pkl file
def save_demo(all_steps, env_name, episode):
    demo_dir = os.path.join('../demos', env_name)
    if not os.path.isdir(demo_dir):
        os.mkdir(demo_dir)
    demo_dir = os.path.join(demo_dir, str(episode))
    if not os.path.isdir(demo_dir):
        os.mkdir(demo_dir)
    all_files = os.listdir(demo_dir)
    demo_num = len(all_files)
    demo_file = os.path.join(demo_dir, '{}_{}'.format(env_name, demo_num))
    assert not os.path.isfile(demo_file)

    print('saving demo to: {}'.format(demo_file))

    with open(demo_file, 'w') as f:
        pkl.dump(all_steps, f)

    print('saved')


# save demo as a pkl file
def save_snapshots(env_steps, model_name='', date=''):
    dir = '../snapshots'
    if not os.path.isdir(dir):
        os.mkdir(dir)
    demo_file = os.path.join(dir, f'{model_name}_{date}')

    print('saving demo to: {}'.format(demo_file))

    # hf = h5py.File('{demo_file}.h5', 'w')

    with open(demo_file, 'w') as f:
        pkl.dump(env_steps, f)

    print('saved')


def open_demo(demo_file):
    assert os.path.isfile(demo_file)

    with open(demo_file) as f:
        demo = pkl.load(f)
        print('num_steps in demo: {}'.format(len(demo)))
        return demo


def get_step(step_num, demo_file):
    # returns dict with keys: action, grid, agent_carrying, agent_pos
    demo = open_demo(demo_file)
    return demo[step_num]


def get_action(step_num, demo_file):
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
        print('true states')
        for state in demo[step_num]['states']:
            if demo[step_num]['states'][state]:
                print(state)


def print_actions(demo_file):
    demo = open_demo(demo_file)
    for step_num in demo:
        print('{}: {}'.format(step_num,  demo[step_num]['action']))


# demo_file = 'demos/MiniGrid-ThrowLeftovers-8x8-N2-v0/MiniGrid-ThrowLeftovers-8x8-N2-v0_0'
# print_actions(demo_file)
