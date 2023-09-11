# MODIFIED FROM MINIGRID REPO

import os
import pickle as pkl
from enum import IntEnum
from gym import spaces
from gym_minigrid.minigrid import MiniGridEnv
from mini_bddl.actions import ACTION_FUNC_MAPPING
from .objects import *
from .grid import BehaviorGrid, GridDimension, is_obj
from mini_behavior.window import Window
from .utils.utils import AttrDict
from mini_behavior.actions import Pickup, Drop, Toggle, Open, Close
import numpy as np


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
        left = 0
        right = 1
        forward = 2
        toggle = 3
        open = 4
        close = 5
        slice = 6
        cook = 7
        drop_in = 8
        pickup_0 = 9
        pickup_1 = 10
        pickup_2 = 11
        drop_0 = 12
        drop_1 = 13
        drop_2 = 14

    def __init__(
        self,
        mode='primitive',
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
        self.teleop = False  # True only when set manually
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

        action_list = ["left", "right", "forward"]

        for obj_type in num_objs.keys():
            self.objs[obj_type] = []
            for i in range(num_objs[obj_type]):
                obj_name = '{}_{}'.format(obj_type, i)

                if obj_type in OBJECT_CLASS.keys():
                    obj_instance = OBJECT_CLASS[obj_type](name=obj_name)
                else:
                    obj_instance = WorldObj(obj_type, None, obj_name)

                self.objs[obj_type].append(obj_instance)
                self.obj_instances[obj_name] = obj_instance

            # create action space for each obj type
            applicable_actions = obj_instance.actions
            for action_name in applicable_actions:
                action_list.append(obj_type + "/" + action_name)

        super().__init__(grid_size=grid_size,
                         width=width,
                         height=height,
                         max_steps=max_steps,
                         see_through_walls=see_through_walls,
                         agent_view_size=agent_view_size,
                         )

        self.grid = BehaviorGrid(width, height)

        pixel_dim = self.grid.pixel_dim

        # The observation space is different from mini-grid due to the z dimension
        self.observation_space = spaces.Box(
            low=0,
            high=255,
            shape=(self.agent_view_size, self.agent_view_size, pixel_dim),
            dtype='uint8'
        )
        self.observation_space = spaces.Dict({
            'image': self.observation_space
        })

        self.mode = mode
        assert self.mode in ["cartesian", "primitive"]
        if self.mode == "cartesian":
            # action list is used to access string by index
            self.action_list = action_list
            action_dict = {value: index for index, value in enumerate(action_list)}
            self.actions = AttrDict(action_dict)
            self.action_space = spaces.Discrete(len(self.actions))
        else:
            self.actions = MiniBehaviorEnv.Actions
            self.action_space = spaces.Discrete(len(self.actions))

        self.carrying = set()

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
        # To keep the same grid for each episode, call env.seed() with
        # the same seed before calling env.reset()
        self._gen_grid(self.width, self.height)

        self.update_states()
        # generate furniture view
        self.furniture_view = self.grid.render_furniture(tile_size=TILE_PIXELS, obj_instances=self.obj_instances)
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

    def place_obj_pos(self,
                      obj,
                      pos,
                      top=None,
                      size=None,
                      reject_fn=None
                      ):
        """
        Place an object at a specific position in the grid

        :param top: top-left position of the rectangle where to place
        :param size: size of the rectangle where to place
        :param obj: the object to place
        :param pos: the top left of the pos we want the object to be placed
        """

        if top is None:
            top = (0, 0)
        else:
            top = (max(top[0], 0), max(top[1], 0))

        if size is None:
            size = (self.grid.width, self.grid.height)

        width = 1 if obj is None else obj.width
        height = 1 if obj is None else obj.height

        valid = True

        if pos[0] < top[0] or pos[0] > min(top[0] + size[0], self.grid.width - width + 1)\
                or pos[1] < top[1] or pos[1] > min(top[1] + size[1], self.grid.height - height + 1):
            raise NotImplementedError(f'position {pos} not in grid')

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
            raise ValidationErr(f'failed in place_obj at {pos}')

        self.grid.set(*pos, obj)

        if obj:
            self.put_obj(obj, *pos)

        return pos

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

                    # If place door, check if it is blocked by other objects
                    if obj is not None and obj.name == "door":
                        left, right, up, down = 0, 0, 0, 0
                        if (x < self.grid.width-1 and not self.grid.is_empty(x+1, y)) or x == self.grid.width - 1:
                            right = 1
                        if (x > 1 and not self.grid.is_empty(x-1, y)) or x == 0:
                            left = 1
                        if (y < self.grid.height-1 and not self.grid.is_empty(x, y+1)) or y == self.grid.height - 1:
                            down = 1
                        if (y > 1 and not self.grid.is_empty(x, y-1)) or y == 0:
                            up = 1
                        if obj.dir=='horz' and (up or down):
                            valid = False
                            break
                        if obj.dir=='vert' and (left or right):
                            valid = False
                            break
                    # Don't place the object on top of another object
                    else:
                        if not self.grid.is_empty(x, y):
                            valid = False
                            break
                    
                    # Don't place the object next to door

                    if obj is not None and obj.type != "door":
                        if x < self.grid.width-1:
                            fur = self.grid.get_furniture(x+1, y)
                            # print("right", fur)
                            if fur is not None and fur.type == "door":
                                valid = False
                                break
                        if x > 1:
                            fur = self.grid.get_furniture(x-1, y)
                            # print("left", fur)
                            if fur is not None and fur.type == "door":
                                valid = False
                                break
                        if y < self.grid.height-1:
                            fur = self.grid.get_furniture(x, y+1)
                            # print("down", fur)
                            if fur is not None and fur.type == "door":
                                valid = False
                                break
                        if y > 1:
                            fur = self.grid.get_furniture(x, y-1)
                            # print("top", fur)
                            if fur is not None and fur.type == "door":
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
        self.grid.set(i, j, obj, dim)
        obj.init_pos = (i, j)
        obj.update_pos((i, j))

        if obj.is_furniture():
            for pos in obj.all_pos:
                self.grid.set(*pos, obj, dim)

    def teleop_mode(self):
        self.teleop = True

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
        self.last_action = action

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
            for dim in fwd_cell:
                for obj in dim:
                    if is_obj(obj) and not obj.can_overlap:
                        can_overlap = False
                        break
            if can_overlap:
                self.agent_pos = fwd_pos
            else:
                self.action_done = False

        # Handle manipulation action based on action space type (mode)
        else:
            if self.mode == "primitive":
                action = self.actions(action)
                action_name = action.name
                if "pickup" in action_name or "drop" in action_name:
                    action_dim = action_name.split('_')  # list: [action, dim]
                    action_class = ACTION_FUNC_MAPPING[action_dim[0]]
                else:
                    action_class = ACTION_FUNC_MAPPING[action_name]
                self.action_done = False

                # Pickup involves certain dimension
                if "pickup" in action_name:
                    for obj in fwd_cell[int(action_dim[1])]:
                        if is_obj(obj) and action_class(self).can(obj):
                            action_class(self).do(obj)
                            self.action_done = True
                            break
                # Drop act on carried object
                elif "drop" in action_name:
                    for obj in self.carrying:
                        if action_class(self).can(obj):
                            drop_dim = obj.available_dims
                            if action_dim[1] == "in":
                                # For drop_in, we don't care about dimension
                                action_class(self).do(obj, np.random.choice(drop_dim))
                                self.action_done = True
                            elif int(action_dim[1]) in drop_dim:
                                action_class(self).do(obj, int(action_dim[1]))
                                self.action_done = True
                            break
                # Everything else act on the forward cell
                else:
                    for dim in fwd_cell:
                        for obj in dim:
                            if is_obj(obj) and action_class(self).can(obj):
                                action_class(self).do(obj)
                                self.action_done = True
                                break
                        if self.action_done:
                            break
            else:
                assert self.mode == "cartesian"
                # Cartesian teleoperation action space needs special care
                if self.teleop:
                    self.last_action = None
                    if action == 'choose':
                        choices = self.all_reachable()
                        if not choices:
                            print("No reachable objects")
                        else:
                            # get all reachable objects
                            text = ''.join('{}) {} \n'.format(i, choices[i].name) for i in range(len(choices)))
                            obj = input("Choose one of the following reachable objects: \n{}".format(text))
                            obj = choices[int(obj)]
                            assert obj is not None, "No object chosen"

                            actions = []
                            for action in MiniBehaviorEnv.Actions:
                                action_name = action.name
                                # process the pickup action
                                if "pickup" in action_name:
                                    if action_name == "pickup_0":
                                        action_name = "pickup"
                                    else:
                                        continue
                                action_class = ACTION_FUNC_MAPPING.get(action_name, None)
                                if action_class and action_class(self).can(obj):
                                    actions.append(action_name)

                            if len(actions) == 0:
                                print("No actions available")
                            else:
                                text = ''.join('{}) {} \n'.format(i, actions[i]) for i in range(len(actions)))

                                action = input("Choose one of the following actions: \n{}".format(text))
                                action = actions[int(action)]  # action name

                                if action == 'drop' or action == 'drop_in':
                                    dims = ACTION_FUNC_MAPPING[action](self).drop_dims(fwd_pos)
                                    spots = ['bottom', 'middle', 'top']
                                    text = ''.join(f'{dim}) {spots[dim]} \n' for dim in dims)
                                    dim = input(f'Choose which dimension to drop the object: \n{text}')
                                    ACTION_FUNC_MAPPING[action](self).do(obj, int(dim))
                                else:
                                    ACTION_FUNC_MAPPING[action](self).do(obj)  # perform action
                                # TODO: this may not be right
                                self.last_action = action

                    # Done action (not used by default)
                    else:
                        assert False, "unknown action {}".format(action)
                else:
                    obj_action = self.action_list[action].split('/')  # list: [obj, action]
                    objs = self.objs[obj_action[0]]
                    action_class = ACTION_FUNC_MAPPING[obj_action[1]]
    
                    self.action_done = False
                    for obj in objs:
                        if action_class(self).can(obj):
                            # Drop to a random dimension
                            if "drop" in obj_action[1]:
                                drop_dim = obj.available_dims
                                action_class(self).do(obj, np.random.choice(drop_dim))
                            else:
                                action_class(self).do(obj)
                            self.action_done = True
                            break

        self.update_states()
        reward = self._reward()
        done = self._end_conditions() or self.step_count >= self.max_steps
        obs = self.gen_obs()

        return obs, reward, done, {}

    def _reward(self):
        if self._end_conditions():
            return 1
        else:
            return 0

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

        if self.render_dim is None:
            img = self.render_furniture_states(img)
        else:
            img = self.render_furniture_states(img, dim=self.render_dim)

        if self.window:
            self.window.set_inventory(self)

        if mode == 'human':
            self.window.set_caption(self.mission)
            self.window.show_img(img)

        return img

    def render_states(self, tile_size=TILE_PIXELS):
        pos = self.front_pos
        imgs = []
        furniture = self.grid.get_furniture(*pos)
        img = np.zeros(shape=(tile_size, tile_size, 3), dtype=np.uint8)
        if furniture:
            furniture.render(img)
            state_values = furniture.get_ability_values(self)
            GridDimension.render_furniture_states(img, state_values)
        imgs.append(img)

        for grid in self.grid.grid:
            furniture, obj = grid.get(*pos)
            state_values = obj.get_ability_values(self) if obj else None
            print(state_values)
            img = GridDimension.render_tile(furniture, obj, state_values, draw_grid_lines=False)
            imgs.append(img)

        return imgs

    def render_furniture_states(self, img, tile_size=TILE_PIXELS, dim=None):
        for obj in self.obj_instances.values():
            if obj.is_furniture():
                if dim is None or dim in obj.dims:
                    i, j = obj.cur_pos
                    ymin = j * tile_size
                    ymax = (j + obj.height) * tile_size
                    xmin = i * tile_size
                    xmax = (i + obj.width) * tile_size
                    sub_img = img[ymin:ymax, xmin:xmax, :]
                    state_values = obj.get_ability_values(self)
                    GridDimension.render_furniture_states(sub_img, state_values)
        return img

    def switch_dim(self, dim):
        self.render_dim = dim
        self.grid.render_dim = dim
