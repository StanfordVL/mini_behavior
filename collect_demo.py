import gym
import pickle as pkl
import os

from mini_behavior.window import Window

# Size in pixels of a tile in the full-scale human view
TILE_PIXELS = 32
seed = 1337
demo = {}
step_count = 0

ALL_DEMOS_DIR = '/Users/emilyjin/Code/behavior/mini_behavior/demos'

def show_states():
    imgs = env.render_states()
    window.show_closeup(imgs)

def save_demo(demo):
    task_dir = os.path.join(ALL_DEMOS_DIR, task)
    if not os.path.isdir(task_dir):
        os.mkdir(task_dir)
    demo_dir = os.path.join(task_dir, str(8))
    if not os.path.isdir(demo_dir):
        os.mkdir(demo_dir)
    demo_file = f'episode_{env.episode}'
    out_file = os.path.join(demo_dir, demo_file)
    with open(out_file, 'wb') as f:
        pkl.dump(demo, f)


def redraw():
    img = env.render('rgb_array', tile_size=TILE_PIXELS)

    window.no_closeup()
    window.set_inventory(env)
    window.show_img(img)


def reset():
    obs = env.reset()

    if hasattr(env, 'mission'):
        print('Mission: %s' % env.mission)
        window.set_caption(env.mission)

    redraw()

    return obs


def step(action):
    state = env.gen_obs()

    obs, reward, done, info = env.step(action)
    demo[env.step_count] = (state, action)

    # print(state)
    # print(action)

    print('step=%s, reward=%.2f' % (env.step_count, reward))

    if done:
        print('done!')
        # save_demo(demo)
        # reset()
    else:
        redraw()


def key_handler(event):
    print('pressed', event.key)
    if event.key == 'escape':
        window.close()
        return
    if event.key == 'left':
        step(env.actions.left)
        return
    if event.key == 'right':
        step(env.actions.right)
        return
    if event.key == 'up':
        step(env.actions.forward)
        return
    if event.key == '1':
        step(env.actions.pickup)
        return
    if event.key == '2':
        step(env.actions.drop)
        return
    if event.key == '3':
        step(env.actions.toggle)
        return
    if event.key == 'pagedown':
        show_states()
        return
# task = 'SimpleInstallingAPrinterTwo'
# env_name = f'MiniGrid-{task}-16x16-N2-v0'
# task = 'SimpleInstallingAPrinter_TwoRooms'
# env_name = 'MiniGrid-SimpleInstallingAPrinterTwo-8x8-N2-v0'
# task = 'SimpleInstallingAPrinter_Distract'
# env_name = 'MiniGrid-SimpleInstallingAPrinterDistract-16x16-N2-v0'
env_name = 'MiniGrid-SimpleInstallingAPrinter-8x8-N2-v0'
env = gym.make(env_name)
env.seed(seed)

window = Window('mini_behavior - ' + env_name)
window.reg_key_handler(key_handler)


init_obs = reset()
print(init_obs)

# Blocking event loop
window.show(block=True)
