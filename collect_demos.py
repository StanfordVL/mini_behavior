import os
import json


def all_pos(env):
    pos = {'agent': [int(obj_pos) for obj_pos in env.agent.cur_pos]}

    for obj_name in env.obj_instances:
        obj_instance = env.obj_instances[obj_name]
        pos[obj_name] = [int(obj_pos) for obj_pos in obj_instance.cur_pos]
    return pos


def all_states(env):
    states = {}
    # save value of each possible state
    for obj_name in env.obj_instances:
        obj_instance = env.obj_instances[obj_name]
        for state in obj_instance.states:
            state_instance = obj_instance.states[state]
            if state_instance.type == 'absolute':
                state_name = '{}/{}'.format(obj_name, state)
                state_value = state_instance.get_value(env)
                states[state_name] = state_value
                states[state_name] = state_value
            elif state_instance.type == 'static':
                state_name = '{}/{}'.format(obj_name, state)
                state_value = state_instance.get_value()
                states[state_name] = state_value
                states[state_name] = state_value
            elif state_instance.type == 'relative':
                for obj2_name in env.obj_instances:
                    obj2_instance = env.obj_instances[obj2_name]
                    if state in obj2_instance.states:
                        state_name = '{}/{}/{}'.format(obj_name, obj2_name, state)
                        state_value = state_instance.get_value(obj2_instance, env)
                        states[state_name] = state_value
    return states

# save last action, all states
def save_step(all_steps, env):
    step_count = env.step_count
    if env.last_action is None:
        action = 'none'
    else:
        action = env.last_action.name
    states = all_states(env)
    pos = all_pos(env)

    all_steps[step_count] = {'action': action,
                             'states': states,
                             'pos': pos
                             }


def save_demo(all_steps, env_name):
    demo_dir = os.path.join('demos', env_name)
    if not os.path.isdir(demo_dir):
        os.mkdir(demo_dir)
    all_files = os.listdir(demo_dir)
    demo_num = len(all_files)
    demo_file = os.path.join(demo_dir, '{}_{}'.format(env_name, demo_num))
    assert not os.path.isfile(demo_file)

    print('saving demo to: {}'.format(demo_file))

    with open(demo_file, 'w') as f:
        json.dump(all_steps, f)

    print('saved')


def open_demo(demo_file):
    assert os.path.isfile(demo_file)

    with open(demo_file) as f:
        demo = json.load(f)
        print('num_steps in demo: {}'.format(len(demo)))
        return demo


def get_step(step_num, demo_file):
    # returns dict with keys: action, states
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
