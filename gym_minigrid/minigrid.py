# MODIFIED FROM MINIGRID REPO

import hashlib
import gym
import os
import pickle as pkl
from enum import IntEnum
from gym import spaces
from gym.utils import seeding
from .utils.globals import COLOR_NAMES
from .agent import Agent
from .objects import *
from .bddl import ABILITIES, ACTION_FUNC_MAPPING
from .grid import Grid, GridDimension, is_obj

# Size in pixels of a tile in the full-scale human view
TILE_PIXELS = 32


class MiniGridEnv(gym.Env):
    """
    2D grid world game environment
    """

    metadata = {
        'render.modes': ['human', 'rgb_array'],
        'video.frames_per_second': 10
    }

    # Enumeration of possible actions
    class Actions(IntEnum):
        # Turn left, turn right, move forward
        left = 0
        right = 1
        forward = 2
        pickup = 3
        drop = 4
        drop_in = 5
        toggle = 6
        open = 7
        close = 8
        slice = 9
        cook = 10

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
    ):
        self.episode = 0
        self.mode = mode
        self.last_action = None
        self.action_done = None

        self.render_dim = None

        # Can't set both grid_size and width/height
        if grid_size:
            assert width is None and height is None
            width = grid_size
            height = grid_size

        if num_objs is None:
            num_objs = {}

        self.objs = {}
        self.obj_instances = {}

        for obj in num_objs.keys():
            self.objs[obj] = []
            for i in range(num_objs[obj]):
                obj_name = '{}_{}'.format(obj, i)
                obj_instance = OBJECT_CLASS[obj](name=obj_name)
                self.objs[obj].append(obj_instance)
                self.obj_instances[obj_name] = obj_instance

        # Action enumeration for this environment, actions are discrete int
        self.actions = MiniGridEnv.Actions
        self.action_space = spaces.Discrete(len(self.actions))

        # Number of cells (width and height) in the agent view
        assert agent_view_size % 2 == 1 and agent_view_size >= 3

        # initialize agent
        self.agent = Agent(self, agent_view_size)

        # Observations are dictionaries containing an
        # encoding of the grid and a textual 'mission' string
        self.observation_space = spaces.Box(
            low=0,
            high=255,
            shape=(self.agent.view_size, self.agent.view_size, 3),
            dtype='uint8'
        )
        self.observation_space = spaces.Dict({
            'image': self.observation_space,
            'mission': spaces.Discrete(1),
            'direction': spaces.Discrete(4),
        })

        # Range of possible rewards
        self.reward_range = (0, math.inf)

        # Window to use for human rendering mode
        self.window = None

        # Environment configuration
        self.width = width
        self.height = height
        self.max_steps = max_steps
        self.see_through_walls = see_through_walls
        self.highlight=highlight

        # Initialize the RNG
        self.seed(seed=seed)

        # Initialize the state
        self.reset()

        # self.mission = ''
        self.furniture_view = None
        # self.state_icons = {state: img_to_array(os.path.join(os.path.dirname(__file__), f'utils/state_icons/{state}.jpg')) for state in ABILITIES}

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
        agent = self.agent.copy()
        objs, obj_instances = self.copy_objs()
        state = {'grid': grid,
                 'agent': agent,
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
            self.agent.load(state['agent'], self.obj_instances)
        return self.grid

    def reset(self):
        # Current position and direction of the agent
        self.agent.reset()

        for obj in self.obj_instances.values():
            obj.reset()

        self.reward = 0

        # Generate a new random grid at the start of each episode
        # To keep the same grid for each episode, call env.seed() with
        # the same seed before calling env.reset()
        self._gen_grid(self.width, self.height)

        # generate furniture view
        self.furniture_view = self.grid.render_furniture(tile_size=TILE_PIXELS, obj_instances=self.obj_instances)

        # These fields should be defined by _gen_grid
        assert self.agent.cur_pos is not None
        assert self.agent.dir is not None

        # Check that the agent doesn't overlap with an object
        # start_cell = self.grid.get(*self.agent.cur_pos)

        assert self.grid.is_empty(*self.agent.cur_pos)

        # Step count since episode start
        self.step_count = 0
        self.episode += 1

        # Return first observation
        obs = self.gen_obs()
        return obs

    def seed(self, seed=1337):
        # Seed the random number generator
        self.np_random, _ = seeding.np_random(seed)
        return [seed]

    def hash(self, size=16):
        """Compute a hash that uniquely identifies the current state of the environment.
        :param size: Size of the hashing
        """
        sample_hash = hashlib.sha256()

        to_encode = [self.grid.encode().tolist(), self.agent.cur_pos, self.agent.dir]
        for item in to_encode:
            sample_hash.update(str(item).encode('utf8'))

        return sample_hash.hexdigest()[:size]

    @property
    def steps_remaining(self):
        return self.max_steps - self.step_count

    def __str__(self):
        """
        Produce a pretty string of the environment's grid along with the agent.
        A grid cell is represented by seed 0_2-character string, the first one for
        the object and the second one for the color.
        """

        # Short string for opened door
        OPENDED_DOOR_IDS = '_'

        # Map agent's direction to short string
        AGENT_DIR_TO_STR = {
            0: '>',
            1: 'V',
            2: '<',
            3: '^'
        }

        str = ''

        for j in range(self.grid.height):
            for i in range(self.grid.width):
                if i == self.agent.cur_pos[0] and j == self.agent.cur_pos[1]:
                    str += 2 * AGENT_DIR_TO_STR[self.agent.dir]
                    continue

                objs = self.grid.get(i, j)

                for c in objs:
                    if c is None:
                        str += '  '
                        continue

                    if c.type == 'door':
                        if c.is_open:
                            str += '__'
                        elif c.is_locked:
                            str += 'L' + c.color[0].upper()
                        else:
                            str += 'D' + c.color[0].upper()
                        continue

                    str += OBJECT_TO_STR[c.type] + c.color[0].upper()

            if j < self.grid.height - 1:
                str += '\n'

        return str

    def _gen_grid(self, width, height):
        self.grid = Grid(width, height)
        self._gen_objs()
        assert self._init_conditions(), "Does not satisfy initial conditions"
        self.place_agent()
        self.mission = self.mission

    def _gen_objs(self):
        assert False, "_gen_objs needs to be implemented by each environment"

    def _reward(self):
        """
        Compute the reward to be given upon success
        """
        assert False, "_reward needs to be implemented by each environment"
        # return 1 - 0.9 * (self.step_count / self.max_steps)

    def _init_conditions(self):
        print('no init conditions')
        return True

    def _end_conditions(self):
        print('no end conditions')
        return False

    def _rand_int(self, low, high):
        """
        Generate random integer in [low,high[
        """

        return self.np_random.randint(low, high)

    def _rand_float(self, low, high):
        """
        Generate random float in [low,high[
        """

        return self.np_random.uniform(low, high)

    def _rand_bool(self):
        """
        Generate random boolean value
        """

        return self.np_random.randint(0, 2) == 0

    def _rand_elem(self, iterable):
        """
        Pick a random element in a list
        """

        lst = list(iterable)
        idx = self._rand_int(0, len(lst))
        return lst[idx]

    def _rand_subset(self, iterable, num_elems):
        """
        Sample a random subset of distinct elements of a list
        """

        lst = list(iterable)
        assert num_elems <= len(lst)

        out = []

        while len(out) < num_elems:
            elem = self._rand_elem(lst)
            lst.remove(elem)
            out.append(elem)

        return out

    def _rand_color(self):
        """
        Generate a random color name (string)
        """

        return self._rand_elem(COLOR_NAMES)

    def _rand_pos(self, xLow, xHigh, yLow, yHigh):
        """
        Generate a random (x,y) position tuple
        """

        return (
            self.np_random.randint(xLow, xHigh),
            self.np_random.randint(yLow, yHigh)
        )

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
                    # if isinstance(obj, FurnitureObj):
                    #     if self.grid.get_furniture(x, y) is not None:
                    #         valid = False
                    #         break
                    # else:
                    #     if self.grid.get_obj(x, y, 0) is not None:
                    #         valid = False
                    #         break

                    # Don't place the object where the agent is
                    if np.array_equal((x, y), self.agent.cur_pos):
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

    def place_agent(
        self,
        top=None,
        size=None,
        rand_dir=True,
        max_tries=math.inf
    ):
        """
        Set the agent's starting point at an empty position in the grid
        """

        self.agent.cur_pos = None

        pos = self.place_obj(None, top, size, max_tries=max_tries)
        self.agent.cur_pos = pos

        if rand_dir:
            self.agent.dir = self._rand_int(0, 4)

        return pos

    def agent_sees(self, x, y):
        """
        Check if a non-empty grid position is visible to the agent
        """

        coordinates = self.agent.relative_coords(x, y)
        if coordinates is None:
            return False
        vx, vy = coordinates

        obs = self.gen_obs()
        obs_grid, _ = Grid.decode(obs['image'])
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
        fwd_pos = self.agent.front_pos
        fwd_cell = self.grid.get(*fwd_pos)

        # Rotate left
        if action == self.actions.left:
            self.agent.dir -= 1
            if self.agent.dir < 0:
                self.agent.dir += 4

        # Rotate right
        elif action == self.actions.right:
            self.agent.dir = (self.agent.dir + 1) % 4

        # Move forward
        elif action == self.actions.forward:
            can_overlap = True
            for dim in fwd_cell:
                for obj in dim:
                    if is_obj(obj) and not obj.can_overlap:
                        can_overlap = False
                        break
            if can_overlap:
                self.agent.cur_pos = fwd_pos
            else:
                self.action_done = False

        else:
            if self.mode == 'human':
                self.last_action = None
                if action == 'choose':
                    choices = self.agent.all_reachable()
                    if not choices:
                        print("No reachable objects")
                    else:
                        # get all reachable objects
                        text = ''.join('{}) {} \n'.format(i, choices[i].name) for i in range(len(choices)))
                        obj = input("Choose one of the following reachable objects: \n{}".format(text))
                        obj = choices[int(obj)]
                        assert obj is not None, "No object chosen"

                        actions = []
                        for action in self.actions:
                            action_class = ACTION_FUNC_MAPPING.get(action.name, None)
                            if action_class and action_class(self).can(obj):
                                actions.append(action.name)

                        if len(actions) == 0:
                            print("No actions available")
                        else:
                            text = ''.join('{}) {} \n'.format(i, actions[i]) for i in range(len(actions)))

                            action = input("Choose one of the following actions: \n{}".format(text))
                            action = actions[int(action)] # action name
                            ACTION_FUNC_MAPPING[action](self).do(obj) # perform action
                            self.last_action = self.actions[action]

                # Done action (not used by default)
                else:
                    assert False, "unknown action {}".format(action)
            else:
                # TODO: with agent centric, how does agent choose which obj to do the action on
                obj_action = self.actions(action).name.split('/') # list: [obj, action]

                # try to perform action
                obj = self.obj_instances[obj_action[0]]
                action_class = ACTION_FUNC_MAPPING[obj_action[1]]

                if action_class(self).can(obj):
                    action_class(self).do(obj)
                else:
                    self.action_done = False

        self.update_states()
        reward = self._reward()
        done = self._end_conditions() or self.step_count >= self.max_steps
        obs = self.gen_obs()

        return obs, reward, done, {}

    def update_states(self):
        for obj in self.obj_instances.values():
            for name, state in obj.states.items():
                if state.type == 'absolute':
                    state._update(self)

    def gen_obs_grid(self):
        """
        Generate the sub-grid observed by the agent.
        This method also outputs a visibility mask telling us which grid
        cells the agent can actually see.
        """
        if self.agent.view_size >= max(self.width, self.height):
            grid = self.grid
        else:
            topX, topY, botX, botY = self.agent.get_view_exts()

            grid = self.grid.slice(topX, topY, self.agent.view_size, self.agent.view_size)

            for i in range(self.agent.dir + 1):
                grid = grid.rotate_left()

        # Process occluders and visibility
        # Note that this incurs some performance cost
        if not self.see_through_walls:
            vis_mask = grid.process_vis(agent_pos=(self.agent.view_size // 2 , self.agent.view_size - 1))
        else:
            vis_mask = np.ones(shape=(grid.width, grid.height), dtype=bool)

        # TODO: Make it so the agent sees what it's carrying
        # We do this by placing the carried object at the agent's position in the agent's partially observable view
        # agent_pos = grid.width // 2, grid.height - 1
        # if self.agent.carrying:
        #     grid.set(*agent_pos, self.agent.carrying)
        # for obj in self.agent.all_reachable():
        #      grid.set(*agent_pos, None)

        return grid, vis_mask

    def gen_obs(self):
        """
        Generate the agent's view (partially observable, low-resolution encoding)
        """

        grid, vis_mask = self.gen_obs_grid()

        # Encode the partially observable view into a numpy array
        image = grid.encode(vis_mask)

        assert hasattr(self, 'mission'), "environments must define a textual mission string"

        # Observations are dictionaries containing:
        # - an image (partially observable view of the environment)
        # - the agent's direction/orientation (acting as a compass)
        # - a textual mission string (instructions for the agent)
        obs = {
            'image': image,
            'direction': self.agent.dir,
            'mission': self.mission
        }

        return obs

    def get_obs_render(self, obs, tile_size=TILE_PIXELS//2):
        """
        Render an agent observation for visualization
        """

        grid, vis_mask = Grid.decode(obs)

        # Render the whole grid
        img = grid.render(
            tile_size,
            agent_pos=(self.agent.view_size // 2, self.agent.view_size - 1),
            agent_dir=3,
            highlight_mask=vis_mask,
        )

        return img

    def render(self, mode='human', close=False, highlight=True, tile_size=TILE_PIXELS):
        """
        Render the whole-grid human view
        """
        highlight = self.highlight

        if close:
            if self.window:
                self.window.close()
            return

        if mode == 'human' and not self.window:
            import gym_minigrid.window
            self.window = gym_minigrid.window.Window('gym_minigrid')
            self.window.show(block=False)

        if self.window:
            self.window.set_inventory(self)

        # Compute which cells are visible to the agent
        _, vis_mask = self.gen_obs_grid()

        # Compute the world coordinates of the bottom-left corner
        # of the agent's view area
        f_vec = self.agent.dir_vec
        r_vec = self.agent.right_vec
        top_left = self.agent.cur_pos + f_vec * (self.agent.view_size-1) - r_vec * (self.agent.view_size // 2)

        # Mask of which cells to highlight
        highlight_mask = np.zeros(shape=(self.width, self.height), dtype=bool)

        # For each cell in the visibility mask
        for vis_j in range(0, self.agent.view_size):
            for vis_i in range(0, self.agent.view_size):
                # If this cell is not visible, don't highlight it
                if not vis_mask[vis_i, vis_j]:
                    continue

                # Compute the world coordinates of this cell
                abs_i, abs_j = top_left - (f_vec * vis_j) + (r_vec * vis_i)

                if abs_i < 0 or abs_i >= self.width:
                    continue
                if abs_j < 0 or abs_j >= self.height:
                    continue

                # Mark this cell to be highlighted
                highlight_mask[abs_i, abs_j] = True

        # Render the whole grid
        if self.render_dim is None:
            img = self.grid.render(
                tile_size,
                self.agent.cur_pos,
                self.agent.dir,
                highlight_mask=highlight_mask if highlight else None
            )

            img = self.render_furniture_states(img)
        else:
            state_values = {obj: obj.get_ability_values(self) for obj in self.obj_instances.values() if not obj.is_furniture()}
            grid = self.grid.grid[self.render_dim]
            img = grid.render(state_values,
                              tile_size,
                              self.agent.cur_pos,
                              self.agent.dir,
                              highlight_mask=highlight_mask if highlight else None)

            img = self.render_furniture_states(img, dim=self.render_dim)
        if mode == 'human':
            self.window.set_caption(self.mission)
            self.window.show_img(img)

        return img

    def render_states(self, tile_size=TILE_PIXELS):
        pos = self.agent.front_pos
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
            img = GridDimension.render_closeup(furniture, obj, state_values)
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

    def close(self):
        if self.window:
            self.window.close()
        return
