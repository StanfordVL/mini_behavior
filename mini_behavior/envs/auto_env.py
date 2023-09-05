
from mini_behavior.floorplan import *
from mini_behavior.roomgrid import *
from mini_behavior.register import register
from mini_behavior.objects import *
import copy
import random


class AutoGenerateEnv(RoomGrid):
    """
    Environment simulate a person left the light on in kitchen
    """

    def __init__(
            self,
            mode='cartesian',
            scene_id='marple_0',
            initial_dict=None,
            max_steps=1e5,
    ):
        self.mission = initial_dict["Grid"]["mission"]

        # configurations for agent generation
        self.initial_dict = initial_dict
        self.state_dict = copy.deepcopy(initial_dict)

        # for auto nums
        self.auto_room_split_dirs = self.initial_dict["Grid"]["auto"]["room_split_dirs"]
        self.auto_min_room_dim = self.initial_dict["Grid"]["auto"]["min_room_dim"]
        self.auto_max_num_room = self.initial_dict["Grid"]["auto"]["max_num_room"]
        # agents
        self.agents = []
        # # furnitures
        # self.furs = {}
        # self.fur_instances = {}
        # objs
        self.objs = {}
        self.obj_instances = {}

        # generate floorplans(rooms), objects, agents
        super().__init__(mode=mode,
                         init_dict=initial_dict,
                         max_steps=max_steps,
                         )

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
                self.floor_plan_walls.append(('vert', (splitIdx, y_min), y_max - y_min + 1))
                tops.append((x_min, y_min))
                sizes.append((splitIdx - x_min, y_max - y_min + 1))
                x_min = splitIdx + 1
            else:
                # Create a horizontal splitting wall
                splitIdx = self._rand_int(
                    y_min + self.auto_min_room_dim, max(y_min + self.auto_min_room_dim + 1, min(3*(y_min + y_max)/2, y_max - (room_num - room_id - 1) * self.auto_min_room_dim)))
                self.floor_plan_walls.append(('horz', (x_min, splitIdx), x_max - x_min + 1))
                tops.append((x_min, y_min))
                sizes.append((x_max - x_min + 1, splitIdx - y_min))
                # horiz generate room with top and size", splitIdx, top, size)
                y_min = splitIdx + 1
        tops.append((x_min, y_min))
        sizes.append((x_max - x_min + 1, y_max - y_min + 1))

        return tops, sizes

    def _gen_objs(self):
        # Gen obj instances from obj dict
        if not self.auto_gen:
            electric_refrigerator = self.objs['electric_refrigerator'][0]
            lettuce = self.objs['lettuce']
            countertop = self.objs['countertop'][0]
            apple = self.objs['apple']
            tomato = self.objs['tomato']
            lights = self.objs['light']
            carving_knife = self.objs['carving_knife'][0]
            plate = self.objs['plate']
            cabinet = self.objs['cabinet'][0]
            sink = self.objs['sink'][0]
            beds = self.objs['bed']
            chairs = self.objs['chair']

            self.objs['electric_refrigerator'][0].width = 1
            self.objs['electric_refrigerator'][0].height = 2

            self.objs['countertop'][0].width = 2
            self.objs['countertop'][0].height = 3

            self.objs['sink'][0].width = 2
            self.objs['sink'][0].height = 2

            self.objs['cabinet'][0].width = 2
            self.objs['cabinet'][0].height = 2

            for bed in self.objs['bed']:
                bed.width = 2
                bed.height = 3

            for chair in self.objs['chair']:
                chair.width = 1
                chair.height = 1

            room_tops = [(1, 1), (9, 1), (1, 23)]
            room_sizes = [(4, 10), (5, 10), (8, 6)]
            kitchen_top = (9, 12)
            kitchen_size = (5, 7)
            bathroom_top = (10, 23)
            bathroom_size = (4, 6)

            self.place_obj(countertop, kitchen_top, kitchen_size)
            self.place_obj(electric_refrigerator, kitchen_top, kitchen_size)
            self.place_obj(cabinet, kitchen_top, kitchen_size)
            self.place_obj(sink, bathroom_top, bathroom_size)
            for i, bed in enumerate(beds):
                self.place_obj(bed, room_tops[i], room_sizes[i])
                self.place_obj(chairs[i], room_tops[i], room_sizes[i])
                self.place_obj(lights[i], room_tops[i], room_sizes[i])

            self.place_obj(lights[-1], kitchen_top, kitchen_size)

            countertop_pos = random.sample(countertop.all_pos, 6)
            self.put_obj(lettuce[0], *countertop_pos[0])
            self.put_obj(lettuce[1], *countertop_pos[1])
            self.put_obj(apple[0], *countertop_pos[2])
            self.put_obj(apple[1], *countertop_pos[3])

            fridge_pos = random.sample(electric_refrigerator.all_pos, 2)
            self.put_obj(tomato[0], *fridge_pos[0])
            self.put_obj(tomato[1], *fridge_pos[1])

            cabinet_pos = random.sample(cabinet.all_pos, 3)
            self.put_obj(plate[0], *cabinet_pos[0])
            plate[0].states['dustyable'].set_value(False)
            self.put_obj(plate[1], *cabinet_pos[1])
            plate[1].states['dustyable'].set_value(False)
            self.put_obj(carving_knife, *cabinet_pos[2])
        else:
            for room in self.room_instances:
                for fur in room.furnitures:
                    self.place_obj(fur, room.top, room.size)
                    if fur.type not in ['light', 'chair', 'Shower']:
                        fur_pos = self._rand_subset(
                            fur.all_pos, len(fur.objects))
                        for i, obj in enumerate(fur.objects):
                            self.put_obj(obj, *fur_pos[i])
                            abilities = self._rand_subset(ABILITIES, 3)
                            for ability in abilities:
                                if ability in list(obj.states.keys()):
                                    obj.states[ability].set_value(True)

    def _reward(self):
        return 0

    def _init_conditions(self):
        for obj_type in ['printer', 'table']:
            assert obj_type in self.objs.keys(), f"No {obj_type}"

        printer = self.objs['printer'][0]

        assert printer.check_abs_state(self, 'onfloor')
        assert not printer.check_abs_state(self, 'toggleable')

        return True

    def _end_conditions(self):
        printer = self.objs['printer'][0]
        table = self.objs['table'][0]

        if printer.check_rel_state(self, table, 'onTop') and printer.check_abs_state(self, 'toggleable'):
            return True
        else:
            return False


# non human input env
register(
    id='MiniGrid-AutoGenerate-16x16-N2-v0',
    entry_point='mini_behavior.envs:AutoGenerateEnv'
)

# human input env
register(
    id='MiniGrid-AutoGenerate-16x16-N2-v1',
    entry_point='mini_behavior.envs:AutoGenerateEnv',
    kwargs={'mode': 'cartesian'}
)
