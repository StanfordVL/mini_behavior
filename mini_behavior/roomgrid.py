# FROM MINIGRID REPO

from .minibehavior import *
from .utils.globals import COLOR_NAMES
from mini_bddl import *

def reject_next_to(env, pos):
    """
    Function to filter out object positions that are right next to
    the agent's starting point
    """

    sx, sy = env.agent_pos
    x, y = pos
    d = abs(sx - x) + abs(sy - y)
    return d < 2


class Room:
    def __init__(
        self,
        top,
        size,
        row=None,
        col=None
    ):
        # Top-left corner and size (tuples)
        self.top = top
        self.size = size

        # List of door objects and door positions
        # Order of the doors is right, down, left, up
        self.doors = [None] * 4
        self.door_pos = [None] * 4

        # List of rooms adjacent to this one
        # Order of the neighbors is right, down, left, up
        self.neighbors = [None] * 4

        # Indicates if this room is behind a locked door
        self.locked = False

        # List of objects contained
        self.objs = []

        self.row = row
        self.col = col

    def reset(self):
        self.doors = [None] * 4
        self.door_pos = [None] * 4
        self.neighbors = [None] * 4
        self.objs = []

    def rand_pos(self, env):
        topX, topY = self.top
        sizeX, sizeY = self.size
        return env._randPos(
            topX + 1, topX + sizeX - 1,
            topY + 1, topY + sizeY - 1
        )

    def pos_inside(self, x, y):
        """
        Check if a position is within the bounds of this room
        """

        topX, topY = self.top
        sizeX, sizeY = self.size

        if x < topX or y < topY:
            return False

        if x >= topX + sizeX or y >= topY + sizeY:
            return False

        return True


class RoomGrid(MiniBehaviorEnv):
    """
    Environment with multiple rooms and random objects.
    This is meant to serve as a base class for other environments.
    """

    def __init__(
        self,
        mode='primitive',
        num_objs=None,
        room_size=10,
        num_rows=2,
        num_cols=2,
        max_steps=1e4,
        see_through_walls=True,
        seed=500,
        agent_view_size=7,
        highlight=True,
        init_dict=None,
        dense_reward=False,
    ):
        if init_dict:
            self.init_dict = init_dict
            height = self.init_dict['Grid']['height']
            width = self.init_dict['Grid']['width']
            # for auto nums
            self.auto_room_split_dirs = self.init_dict["Grid"]["auto"]["room_split_dirs"]
            self.auto_min_room_dim = self.init_dict["Grid"]["auto"]["min_room_dim"]
            self.auto_max_num_room = self.init_dict["Grid"]["auto"]["max_num_room"]
        else:
            assert room_size > 0
            assert room_size >= 3
            assert num_rows > 0
            assert num_cols > 0
            self.room_size = room_size
            self.num_rows = num_rows
            self.num_cols = num_cols

            height = (room_size - 1) * num_rows + 1
            width = (room_size - 1) * num_cols + 1
            self.init_dict = None

        super().__init__(
            mode=mode,
            width=width,
            height=height,
            num_objs=num_objs,
            max_steps=max_steps,
            see_through_walls=see_through_walls,
            seed=seed,
            agent_view_size=agent_view_size,
            highlight=highlight,
            dense_reward=dense_reward,
        )
    
    def add_walls(self, width, height):
        # Generate the surrounding walls
        # self.objs = {}
        # self.obj_instances = {}
        self.grid.wall_rect(0, 0, width, height)
        for dir, (x, y), length in self.floor_plan_walls:
            if dir == 'horz':
                self.grid.horz_wall(x, y, length)
            else:
                self.grid.vert_wall(x, y, length)

        obj_type = "door"
        door_count = 0
        for dir, (x, y), length in self.floor_plan_walls:
            if door_count >= len(self.room_instances) - 1:
                break
            if dir == 'horz' and 0 < y < height - 1:
                # open_status = self._rand_bool()
                open_status = False
                if obj_type not in self.objs:
                    self.objs[obj_type] = []
                obj_name = f'{obj_type}_{len(self.objs[obj_type])}'
                door = Door(dir, is_open=open_status)
                self.objs[obj_type].append(door)
                door.id = len(self.obj_instances) + 1
                self.obj_instances[obj_name] = door
                self.place_obj(door, (x, y), (length, 1), max_tries=20)
                door_count += 1
            elif dir == 'vert' and 0 < x < width - 1:
                # open_status = self._rand_bool()
                open_status = False
                if obj_type not in self.objs:
                    self.objs[obj_type] = []
                obj_name = f'{obj_type}_{len(self.objs[obj_type])}'
                door = Door(dir, is_open=open_status)
                self.objs[obj_type].append(door)
                door.id = len(self.obj_instances) + 1
                self.obj_instances[obj_name] = door
                self.place_obj(door, (x, y), (1, length), max_tries=20)
                # self.grid.set(x, doorIdx, door)
                door_count += 1
            else:
                continue

    def _gen_floorplan(self):
        # floor plan
        self.floor_plan_walls = []
        # rooms
        self.room_instances = []

        # num rooms
        if self.init_dict['Grid']['rooms']['num'] is not None:
            num_room = self.init_dict['Grid']['rooms']['num']
        else:
            num_room = self._rand_int(1, self.auto_max_num_room)

        room_initial = self.init_dict['Grid']['rooms']['initial']

        # check if generate floor plan automatically or room sizes have been decided
        auto_floor_plan = True
        if room_initial and room_initial[0]['top'] is not None:
            assert len(
                room_initial) == num_room, 'Please specify all room initials, tops and size'
            for room_init in room_initial:
                if room_init['top'] is None or room_init['size'] is None:
                    raise Exception(
                        'Please specify all room tops and sizes')
            auto_floor_plan = False

        if auto_floor_plan:
            tops, sizes = self._gen_random_floorplan(num_room)
        
        for num in range(num_room):
            if num < len(room_initial):
                if auto_floor_plan:
                    top = tops[num]
                    size = sizes[num]
                else:
                    top = room_initial[num]['top']
                    size = room_initial[num]['size']
                    self.floor_plan_walls.append(
                        ('vert', (top[0] - 1, top[1]), size[1] + 1))
                    self.floor_plan_walls.append(
                        ('vert', (top[0] + size[0], top[1] - 1), size[1] + 1))
                    self.floor_plan_walls.append(
                        ('horz', (top[0] - 1, top[1] - 1), size[0] + 1))
                    self.floor_plan_walls.append(
                        ('horz', (top[0], top[1] + size[1]), size[0] + 1))
            else:
                top = tops[num]
                size = sizes[num]

            self._gen_room(top, size)
    
    def _gen_random_floorplan(self, room_num):
        x_min, y_min, x_max, y_max = 1, 1, self.width-2, self.height-2
        tops = []
        sizes = []
        for room_id in range(room_num-1):
            cur_dir = self._rand_subset(self.auto_room_split_dirs, 1)[0]
            if cur_dir == 'vert':
                # Create a vertical splitting wall
                splitIdx = self._rand_int(
                    x_min + self.auto_min_room_dim, max(x_min + self.auto_min_room_dim + 1, min(3*(x_min + x_max)/2, x_max - (room_num - room_id - 1) * self.auto_min_room_dim)))
                self.floor_plan_walls.append(('vert', (splitIdx, y_min), None))
                tops.append((x_min, y_min))
                sizes.append((splitIdx - x_min, y_max - y_min + 1))
                x_min = splitIdx + 1
            else:
                # Create a horizontal splitting wall
                splitIdx = self._rand_int(
                    y_min + self.auto_min_room_dim, max(y_min + self.auto_min_room_dim + 1, min(3*(y_min + y_max)/2, y_max - (room_num - room_id - 1) * self.auto_min_room_dim)))
                self.floor_plan_walls.append(('horz', (x_min, splitIdx), None))
                tops.append((x_min, y_min))
                sizes.append((x_max - x_min + 1, splitIdx - y_min))
                # horiz generate room with top and size", splitIdx, top, size)
                y_min = splitIdx + 1
        tops.append((x_min, y_min))
        sizes.append((x_max - x_min + 1, y_max - y_min + 1))

        return tops, sizes

    def _gen_room(self, top, size):
        room = Room(top=top, size=size)
        self.room_instances.append(room)

    def _gen_random_objs(self):
        # objs
        self.objs = {}
        self.obj_instances = {}

        self.add_walls(self.width, self.height)

        for room_id, room in enumerate(self.room_instances):
            # Generate furs and objs for the room
            if room_id < len(self.init_dict['Grid']['rooms']['initial']) and self.init_dict['Grid']['rooms']['initial'][room_id]['furnitures']['num'] is not None:
                num_furs = self.init_dict['Grid']['rooms']['initial'][room_id]['furnitures']['num']
            else:
                num_furs = self._rand_int(
                    1, max(2, int(room.size[0]*room.size[1]/12)))

            if room_id < len(self.init_dict['Grid']['rooms']['initial']) and self.init_dict['Grid']['rooms']['initial'][room_id]['furnitures'] is not None:
                furniture_initial = self.init_dict['Grid']['rooms']['initial'][room_id]['furnitures']['initial']
            else:
                furniture_initial = []
            # room.num_furs = num_furs
            # room.self_id = room_id

            for fur_id in range(num_furs):
                if fur_id < len(furniture_initial) and furniture_initial[fur_id]['type'] is not None:
                    furniture_type = furniture_initial[fur_id]['type']
                else:
                    furniture_type = self._rand_subset(
                        FURNITURE, 1)[0]

                # generate furniture instance
                if furniture_type not in self.objs:
                    self.objs[furniture_type] = []
                fur_name = f'{furniture_type}_{len(self.objs[furniture_type])}'
                if furniture_type in OBJECT_CLASS.keys():
                    fur_instance = OBJECT_CLASS[furniture_type](
                        name=fur_name)
                else:
                    fur_instance = WorldObj(furniture_type, None, fur_name)

                fur_instance.in_room = room
                self.objs[furniture_type].append(fur_instance)
                fur_instance.id = len(self.obj_instances) + 1
                self.obj_instances[fur_name] = fur_instance
                room.objs.append(fur_instance)

                # place furniture
                if fur_id < len(furniture_initial) and furniture_initial[fur_id]['pos'] is not None:
                    pos = self.place_obj_pos(
                        fur_instance, pos=furniture_initial[fur_id]['pos'], top=room.top, size=room.size)
                else:
                    pos = self.place_obj(fur_instance, room.top, room.size)

                # set furniture states
                if fur_id < len(furniture_initial) and furniture_initial[fur_id]['state'] is not None:
                    states = furniture_initial[fur_id]['state']
                    for state_name, flag in states:
                        if flag:
                            fur_instance.states[state_name].set_value(
                                True)
                else:
                    num_ability = self._rand_int(0, len(ABILITIES))
                    abilities = self._rand_subset(
                        ABILITIES, num_ability)
                    for ability in abilities:
                        if ability in list(fur_instance.states.keys()):
                            fur_instance.states[ability].set_value(
                                True)
                fur_instance.update(self)
                # for every furniture, generate objs on it
                if furniture_type not in FURNITURE_CANNOT_ON and fur_instance.width * fur_instance.height > 1:
                    if fur_id < len(furniture_initial) and furniture_initial[fur_id]['objs'] is not None:
                        obj_initial = furniture_initial[fur_id]['objs']['initial']
                        if furniture_initial[fur_id]['objs']['num'] is not None:
                            num_objs = furniture_initial[fur_id]['objs']['num']
                        else:
                            num_objs = max(len(obj_initial), self._rand_int(
                                1, max(1, fur_instance.width * fur_instance.height)))
                    else:
                        num_objs = self._rand_int(
                            1, max(1, fur_instance.width * fur_instance.height))
                        obj_initial = []

                    obj_poses = set()
                    for obj_id in range(num_objs):
                        if obj_id < len(obj_initial) and obj_initial[obj_id]['type'] is not None:
                            obj_type = obj_initial[obj_id]['type']
                        else:
                            OBJECT_LIST = [x for x in OBJECTS if x not in FURNITURE]
                            obj_type = self._rand_subset(
                                OBJECT_LIST, 1)[0]
                        if obj_type not in self.objs:
                            self.objs[obj_type] = []
                        obj_name = f'{obj_type}_{len(self.objs[obj_type])}_{fur_instance.name}'

                        # generate obj instance
                        if obj_type in OBJECT_CLASS.keys():
                            obj_instance = OBJECT_CLASS[obj_type](
                                name=obj_name)
                        else:
                            obj_instance = WorldObj(
                                obj_type, None, obj_name)
                        obj_instance.in_room = room
                        obj_instance.on_fur = fur_instance

                        self.objs[obj_type].append(obj_instance)
                        obj_instance.id = len(self.obj_instances) + 1
                        self.obj_instances[obj_name] = obj_instance
                        room.objs.append(obj_instance)

                        # put obj instance
                        if obj_id < len(obj_initial) and obj_initial[obj_id]['pos'] is not None:
                            pos = obj_initial[obj_id]['pos']
                            self.put_obj(obj_instance, *pos)
                            obj_poses.add(pos)
                        else:
                            pos = self._rand_subset(
                                fur_instance.all_pos, 1)[0]
                            while pos in obj_poses:
                                pos = self._rand_subset(
                                    fur_instance.all_pos, 1)[0]
                            self.put_obj(obj_instance, *pos)
                            obj_poses.add(pos)

                        # set obj states
                        if obj_id < len(obj_initial) and obj_initial[obj_id]['state'] is not None:
                            states = obj_initial[obj_id]['state']
                            for state_name, flag in states:
                                if flag:
                                    obj_instance.states[state_name].set_value(
                                        True)
                        else:
                            num_ability = self._rand_int(0, len(ABILITIES))
                            abilities = self._rand_subset(
                                ABILITIES, num_ability)
                            for ability in abilities:
                                if ability in list(obj_instance.states.keys()):
                                    obj_instance.states[ability].set_value(
                                        True)
                        obj_instance.update(self)

    def _gen_objs(self):
        # Gen obj instances from obj dict
        if not self.init_dict:
            self._gen_env_objs()
        else:
            for room in self.room_instances:
                for fur in room.furnitures:
                    self.place_obj(fur, room.top, room.size)
                    if fur.type not in FURNITURE_CANNOT_ON:
                        fur_pos = self._rand_subset(
                            fur.all_pos, len(fur.objects))
                        for i, obj in enumerate(fur.objects):
                            self.put_obj(obj, *fur_pos[i])
                            abilities = self._rand_subset(ABILITIES, 3)
                            for ability in abilities:
                                if ability in list(obj.states.keys()):
                                    obj.states[ability].set_value(True)

    def room_num_from_pos(self, x, y):
        i = x // (self.room_size-1)
        j = y // (self.room_size-1)
        room_num = i * self.num_cols + j
        return room_num

    def room_idx_from_num(self, x):
        i = x // self.num_cols
        j = x % self.num_cols
        return i, j

    def room_from_pos(self, x, y):
        """Get the room a given position maps to"""

        assert x >= 0
        assert y >= 0

        i = x // (self.room_size-1)
        j = y // (self.room_size-1)

        assert i < self.num_cols
        assert j < self.num_rows

        return self.room_grid[j][i]

    def get_room(self, i, j):
        assert i < self.num_cols
        assert j < self.num_rows
        return self.room_grid[j][i]

    def reset(self):
        super().reset()
        if self.init_dict:
            for room in self.room_instances:
                    room.reset()
        else:
            for row in self.room_grid:
                for room in row:
                    room.reset()
                    
        return self.gen_obs()

    def _gen_grid(self, width, height):
        if not self.init_dict:
            self._gen_rooms(width, height)
            self._gen_objs()
            self.place_agent()
            self.connect_all()
        else:
            self.grid = BehaviorGrid(width, height)
            self._gen_floorplan()
            self._gen_random_objs()
            self.place_agent_auto()

        

    def _gen_rooms(self, width, height):
        # Create the grid
        self.grid = BehaviorGrid(width, height)
        self.room_grid = [] # list of lists
        self.doors = []

        # For each row of rooms
        for j in range(0, self.num_rows):
            row = []

            # For each column of rooms
            for i in range(0, self.num_cols):
                room = Room(
                    top=(i * (self.room_size-1), j * (self.room_size-1)),
                    size=(self.room_size, self.room_size),
                    row=j,
                    col=i
                )
                row.append(room)

                # Generate the walls for this room
                self.grid.wall_rect(*room.top, *room.size)

            self.room_grid.append(row)

        # For each row of rooms
        for j in range(0, self.num_rows):
            # For each column of rooms
            for i in range(0, self.num_cols):
                room = self.room_grid[j][i]

                x_l, y_l = (room.top[0] + 1, room.top[1] + 1)
                x_m, y_m = (room.top[0] + room.size[0] - 1, room.top[1] + room.size[1] - 1)

                # Door positions, order is right, down, left, up
                if i < self.num_cols - 1:
                    room.neighbors[0] = self.room_grid[j][i+1]
                    room.door_pos[0] = (x_m, self._rand_int(y_l, y_m))
                if j < self.num_rows - 1:
                    room.neighbors[1] = self.room_grid[j+1][i]
                    room.door_pos[1] = (self._rand_int(x_l, x_m), y_m)
                if i > 0:
                    room.neighbors[2] = self.room_grid[j][i-1]
                    room.door_pos[2] = room.neighbors[2].door_pos[0]
                if j > 0:
                    room.neighbors[3] = self.room_grid[j-1][i]
                    room.door_pos[3] = room.neighbors[3].door_pos[1]

    def _gen_objs(self):
        assert False, "_gen_objs needs to be implemented by each environment"

    def place_in_room(self, i, j, obj, reject_fn=reject_next_to):
        """
        Add an existing object to room (i, j)
        """

        room = self.get_room(i, j)

        pos = self.place_obj(
            obj,
            room.top,
            room.size,
            reject_fn=reject_fn,
            max_tries=1000
        )

        room.objs.append(obj)

        return obj, pos

    # def add_object(self, i, j, kind=None, color=None):
    #     """
    #     Add a new object to room (i, j)
    #     """
    #
    #     if kind is None:
    #         kind = self._rand_elem(['key', 'ball', 'box'])
    #
    #     if color is None:
    #         color = self._rand_color()
    #
    #     # TODO: we probably want to add an Object.make helper function
    #     assert kind in OBJECTS
    #     obj = OBJECT_CLASS[kind]()
    #
    #     return self.place_in_room(i, j, obj)

    def add_door(self, i, j, door_idx=None, color=None, locked=None):
        """
        Add a door to a room, connecting it to a neighbor
        """

        room = self.get_room(i, j)

        if door_idx is None:
            # Need to make sure that there is a neighbor along this wall
            # and that there is not already a door
            while True:
                door_idx = self._rand_int(0, 4)
                if room.neighbors[door_idx] and room.doors[door_idx] is None:
                    break

        if color is None:
            color = self._rand_color()

        if locked is None:
            locked = self._rand_bool()

        assert room.doors[door_idx] is None, "door already exists"

        room.locked = locked

        name = 'door_{}'.format(len(self.doors))
        door = Door(is_open=True)
        self.doors.append(door)

        pos = room.door_pos[door_idx]
        self.grid.set(*pos, door)
        door.cur_pos = pos

        neighbor = room.neighbors[door_idx]
        room.doors[door_idx] = door
        neighbor.doors[(door_idx+2) % 4] = door

        return door, pos

    def remove_wall(self, i, j, wall_idx):
        """
        Remove a wall between two rooms
        """

        room = self.get_room(i, j)

        assert 0 <= wall_idx < 4
        assert room.doors[wall_idx] is None, "door exists on this wall"
        assert room.neighbors[wall_idx], "invalid wall"

        neighbor = room.neighbors[wall_idx]

        tx, ty = room.top
        w, h = room.size

        # Ordering of walls is right, down, left, up
        if wall_idx == 0:
            for i in range(1, h - 1):
                self.grid.set(tx + w - 1, ty + i, None)
        elif wall_idx == 1:
            for i in range(1, w - 1):
                self.grid.set(tx + i, ty + h - 1, None)
        elif wall_idx == 2:
            for i in range(1, h - 1):
                self.grid.set(tx, ty + i, None)
        elif wall_idx == 3:
            for i in range(1, w - 1):
                self.grid.set(tx + i, ty, None)
        else:
            assert False, "invalid wall index"

        # Mark the rooms as connected
        room.doors[wall_idx] = True
        neighbor.doors[(wall_idx+2) % 4] = True

    def place_agent_auto(
        self,
        top=None,
        size=None,
        rand_dir=True,
        max_tries=math.inf
    ):
        """
        Set the agent's starting point at an empty position in the grid
        """
        
        if self.initial_dict['Grid']['agents']['pos'] is None:
            pos = self.place_obj(None, top, size, max_tries=max_tries)
            self.agent_pos = (pos[0], pos[1])
        else:
            pos = self.initial_dict['Grid']['agents']['pos']
            self.place_obj_pos(None, pos, top, size)
            self.agent_pos = (pos[0], pos[1])

        if self.initial_dict['Grid']['agents']['dir'] is None:
            self.agent_dir = self._rand_int(0, 4)
        else:
            self.agent_dir = self.initial_dict['Grid']['agents']['dir']

        return pos

    def place_agent(self, i=None, j=None, rand_dir=True):
        """
        Place the agent in a room
        """

        if i is None:
            i = self._rand_int(0, self.num_cols)
        if j is None:
            j = self._rand_int(0, self.num_rows)

        room = self.room_grid[j][i]

        # Find a position that is not right in front of an object
        while True:
            super().place_agent(room.top, room.size, rand_dir, max_tries=1000)
            if self.grid.is_empty(*self.front_pos):
                break

        return self.agent_pos


    def connect_all(self, door_colors=COLOR_NAMES, max_itrs=5000):
        """
        Make sure that all rooms are reachable by the agent from its
        starting position
        """
        start_room = self.room_from_pos(*self.agent_pos)

        added_doors = []

        def find_reach():
            reach = set()
            stack = [start_room]
            while len(stack) > 0:
                room = stack.pop()
                if room in reach:
                    continue
                reach.add(room)
                for i in range(0, 4):
                    if room.doors[i]:
                        stack.append(room.neighbors[i])
            return reach

        num_itrs = 0

        while True:
            # This is to handle rare situations where random sampling produces
            # a level that cannot be connected, producing in an infinite loop
            if num_itrs > max_itrs:
                raise RecursionError('connect_all failed')
            num_itrs += 1

            # If all rooms are reachable, stop
            reach = find_reach()
            if len(reach) == self.num_rows * self.num_cols:
                break

            # Pick a random room and door position
            i = self._rand_int(0, self.num_cols)
            j = self._rand_int(0, self.num_rows)
            k = self._rand_int(0, 4)
            room = self.get_room(i, j)

            # if the room is reachable
            if room in reach:
                continue

            # If there is already a door there, skip
            if not room.door_pos[k] or room.doors[k]:
                continue

            if room.locked or room.neighbors[k].locked:
                continue

            color = self._rand_elem(door_colors)
            door, _ = self.add_door(i, j, k, color, False)
            added_doors.append(door)

        return added_doors

    def add_distractors(self, i=None, j=None, num_distractors=10, all_unique=True):
        """
        Add random objects that can potentially distract/confuse the agent.
        """

        # Collect a list of existing objects
        objs = []
        for row in self.room_grid:
            for room in row:
                for obj in room.objs:
                    objs.append((obj.type, obj.color))

        # List of distractors added
        dists = []

        while len(dists) < num_distractors:
            color = self._rand_elem(COLOR_NAMES)
            type = self._rand_elem(['key', 'ball', 'box'])
            obj = (type, color)

            if all_unique and obj in objs:
                continue

            # Add the object to a random room if no room specified
            room_i = i
            room_j = j
            if room_i is None:
                room_i = self._rand_int(0, self.num_cols)
            if room_j is None:
                room_j = self._rand_int(0, self.num_rows)

            dist, pos = self.add_object(room_i, room_j, *obj)

            objs.append(obj)
            dists.append(dist)

        return dists
