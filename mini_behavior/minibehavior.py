# MODIFIED FROM MINIGRID REPO

import os
import pickle as pkl
from enum import IntEnum
from gym import spaces
from gym_minigrid.minigrid import MiniGridEnv
# from bddl.actions import ACTION_FUNC_MAPPING
from .objects import *
from .grid import BehaviorGrid, is_obj
from mini_behavior.mini_behavior.window import Window

# Size in pixels of a tile in the full-scale human view
TILE_PIXELS = 32


class MiniBehaviorEnv(MiniGridEnv):
    """
    2D grid world game environment
    """
    metadata = {
        # Deprecated: use 'render_modes' instead
        "render.modes": ["human", "rgb_array"],
        "video.frames_per_second": 10,  # Deprecated: use 'render_fps' instead
        "render_modes": ["human", "rgb_array", "single_rgb_array"],
        "render_fps": 10,
    }

    # Enumeration of possible actions
    class Actions(IntEnum):
        # Turn left, turn right, move forward
        left = 0
        right = 1
        forward = 2

    def __init__(
        self,
        mode='not_human',
        grid_size=None,
        width=None,
        height=None,
        num_objs=None,
        max_steps=1e5,
        see_through_walls=False,
        seed=1337,
        agent_view_size=7,
        highlight=True,
        tile_size=TILE_PIXELS,
    ):
        self.episode = 0
        self.mode = mode
        self.last_action = None
        self.action_done = None

        self.render_dim = None

        self.highlight = highlight
        self.tile_size = tile_size

        # Initialize the RNG
        self.seed(seed=seed)
        self.furniture_view = None

        if num_objs is None:
            num_objs = {}

        self.objs = {}
        self.obj_instances = {}

        self.add_objs(num_objs)
        # for obj_type in num_objs.keys():
        #     self.objs[obj_type] = []
        #     for i in range(num_objs[obj_type]):
        #         obj_name = '{}_{}'.format(obj_type, i)
        #
        #         if obj_type in OBJECT_CLASS.keys():
        #             obj_instance = OBJECT_CLASS[obj_type](name=obj_name)
        #         else:
        #             obj_instance = WorldObj(obj_type, None, obj_name)
        #
        #         self.objs[obj_type].append(obj_instance)
        #         self.obj_instances[obj_name] = obj_instance

        self.grid = None

        super().__init__(grid_size=grid_size,
                         width=width,
                         height=height,
                         max_steps=max_steps,
                         see_through_walls=see_through_walls,
                         agent_view_size=agent_view_size,
                         )

        # Action enumeration for this environment, actions are discrete int
        self.actions = MiniBehaviorEnv.Actions
        self.action_space = spaces.Discrete(len(self.actions))

        self.carrying = set()

    def add_objs(self, num_objs):
        new_objs = []
        for obj_type in num_objs.keys():
            cur_objs = self.objs.get(obj_type, [])
            n = len(cur_objs)
            for i in range(num_objs[obj_type]):
                obj_name = '{}_{}'.format(obj_type, n + i)
                if obj_type in OBJECT_CLASS.keys():
                    obj_instance = OBJECT_CLASS[obj_type](name=obj_name)
                else:
                    obj_instance = WorldObj(obj_type, None, obj_name)

                cur_objs.append(obj_instance)
                self.obj_instances[obj_name] = obj_instance
                new_objs.append(obj_instance)

            self.objs[obj_type] = cur_objs

        return new_objs

    def copy_objs(self):
        from copy import deepcopy
        return deepcopy(self.objs), deepcopy(self.obj_instances)

    # TODO: check this works
    def load_objs(self, state):
        obj_instances = state['obj_instances']
        grid = state['grid']
        for obj in self.obj_instances.values():
            if type(obj) != Wall and type(obj) != Door:
                load_obj = obj_instances[obj.name]
                obj.load(load_obj, grid, self)

        for obj in self.obj_instances.values():
            obj.contains = []
            for other_obj in self.obj_instances.values():
                if other_obj.check_rel_state(self, obj, 'inside'):
                    obj.contains.append(other_obj)

    # TODO: check this works
    def get_state(self):
        grid = self.grid.copy()
        agent_pos = self.agent_pos
        agent_dir = self.agent_dir
        objs, obj_instances = self.copy_objs()
        state = {'grid': grid,
                 'agent_pos': agent_pos,
                 'agent_dir': agent_dir,
                 'objs': objs,
                 'obj_instances': obj_instances
                 }
        return state

    def save_state(self, out_file='cur_state.pkl'):
        state = self.get_state()
        with open(out_file, 'wb') as f:
            pkl.dump(state, f)
            print(f'saved to: {out_file}')

    # TODO: check this works
    def load_state(self, load_file):
        assert os.path.isfile(load_file)
        with open(load_file, 'rb') as f:
            state = pkl.load(f)
            self.load_objs(state)
            self.grid.load(state['grid'], self)
            self.agent_pos = state['agent_pos']
            self.agent_dir = state['agent_dir']
        return self.grid

    def reset(self):
        # Reinitialize episode-specific variables
        self.agent_pos = (-1, -1)
        self.agent_dir = -1

        self.carrying = set()

        for obj in self.obj_instances.values():
            obj.reset()

        self.reward = 0

        # Generate a new random grid at the start of each episode
        # the same seed before calling env.reset()
        self._gen_grid(self.width, self.height)

        # generate furniture view
        # self.furniture_view = self.grid.render_furniture(tile_size=TILE_PIXELS, obj_instances=self.obj_instances)

        # These fields should be defined by _gen_grid
        assert self.agent_pos is not None
        assert self.agent_dir is not None

        # Check that the agent doesn't overlap with an object
        assert self.grid.is_empty(*self.agent_pos)

        # Step count since episode start
        self.step_count = 0
        self.episode += 1

        # Return first observation
        obs = self.gen_obs()
        return obs

    def _gen_grid(self, width, height):
        self.grid = BehaviorGrid(width, height)
        self._gen_objs()
        assert self._init_conditions(), "Does not satisfy initial conditions"
        self.place_agent()

    def _gen_objs(self):
        assert False, "_gen_objs needs to be implemented by each environment"

    def _init_conditions(self):
        print('no init conditions')
        return True

    def _end_conditions(self):
        print('no end conditions')
        return False

    def place_obj(self,
                  obj,
                  top=None,
                  size=None,
                  reject_fn=None,
                  max_tries=math.inf
    ):
        """
        Place an object at an empty position in the grid

        :param top: top-left position of the rectangle where to place
        :param size: size of the rectangle where to place
        :param reject_fn: function to filter out potential positions
        """

        if top is None:
            top = (0, 0)
        else:
            top = (max(top[0], 0), max(top[1], 0))

        if size is None:
            size = (self.grid.width, self.grid.height)

        num_tries = 0

        while True:
            # This is to handle with rare cases where rejection sampling
            # gets stuck in an infinite loop
            if num_tries > max_tries:
                raise RecursionError('rejection sampling failed in place_obj')

            num_tries += 1

            width = 1 if obj is None else obj.width
            height = 1 if obj is None else obj.height

            pos = np.array((
                self._rand_int(top[0], min(top[0] + size[0], self.grid.width - width + 1)),
                self._rand_int(top[1], min(top[1] + size[1], self.grid.height - height + 1))
            ))

            valid = True

            for dx in range(width):
                for dy in range(height):
                    x = pos[0] + dx
                    y = pos[1] + dy

                    # Don't place the object on top of another object
                    if not self.grid.is_empty(x, y):
                        valid = False
                        break

                    # Don't place the object where the agent is
                    if np.array_equal((x, y), self.agent_pos):
                        valid = False
                        break

                    # Check if there is a filtering criterion
                    if reject_fn and reject_fn(self, (x, y)):
                        valid = False
                        break

            if not valid:
                continue

            break

        self.grid.set(*pos, obj)

        if obj:
            self.put_obj(obj, *pos)

        return pos

    def put_obj(self, obj, i, j, dim=0):
        """
        Put an object at a specific position in the grid
        """
        obj.init_pos = (i, j)
        obj.update_pos((i, j))
        self.grid.set(i, j, obj, dim)

    def agent_sees(self, x, y):
        """
        Check if a non-empty grid position is visible to the agent
        """

        coordinates = self.relative_coords(x, y)
        if coordinates is None:
            return False
        vx, vy = coordinates

        obs = self.gen_obs()
        obs_grid, _ = BehaviorGrid.decode(obs['image'])
        obs_cell = obs_grid.get(vx, vy)
        world_cell = self.grid.get(x, y)

        if obs_grid.is_empty(vx, vy):
            return False

        for i in range(3):
            if [obj.type for obj in obs_cell[i]] != [obj.type for obj in world_cell[i]]:
                return False

        return True

    def step(self, action):
        # keep track of last action
        if self.mode == 'human':
            self.last_action = action
        else:
            self.last_action = self.actions(action)

        self.step_count += 1
        self.action_done = True

        # Get the position and contents in front of the agent
        fwd_pos = self.front_pos
        fwd_cell = self.grid.get(*fwd_pos)

        # Rotate left
        if action == self.actions.left:
            self.agent_dir -= 1
            if self.agent_dir < 0:
                self.agent_dir += 4

        # Rotate right
        elif action == self.actions.right:
            self.agent_dir = (self.agent_dir + 1) % 4

        # Move forward
        elif action == self.actions.forward:
            can_overlap = True
            furniture = fwd_cell.furniture
            objs = fwd_cell.objs
            for obj in [furniture] + objs:
                if is_obj(obj) and not obj.can_overlap:
                    can_overlap = False
                    break
            if can_overlap:
                self.agent_pos = fwd_pos
            else:
                self.action_done = False

        self.update_states()
        reward = self._reward()
        done = self._end_conditions() or self.step_count >= self.max_steps
        obs = self.gen_obs()

        return obs, reward, done, {}

    def all_reachable(self):
        return [obj for obj in self.obj_instances.values() if obj.check_abs_state(self, 'inreachofrobot')]

    def update_states(self):
        for obj in self.obj_instances.values():
            for name, state in obj.states.items():
                if state.type == 'absolute':
                    state._update(self)

        self.grid.state_values = {obj: obj.get_ability_values(self) for obj in self.obj_instances.values()}

    def render(self, mode='human', highlight=True, tile_size=TILE_PIXELS):
        """
        Render the whole-grid human view
        """
        if mode == "human" and not self.window:
            self.window = Window("mini_behavior")
            self.window.show(block=False)

        img = super().render(mode='rgb_array', highlight=highlight, tile_size=tile_size)

        if self.window:
            self.window.set_inventory(self)

        if mode == 'human':
            self.window.set_caption(self.mission)
            self.window.show_img(img)

        return img
