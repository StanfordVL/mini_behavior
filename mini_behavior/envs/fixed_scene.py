# FROM MINIGRID REPO
from mini_behavior.mini_behavior.roomgrid import *
from mini_behavior.mini_behavior.register import register


# TODO: use procthor to generate env

class FixedEnv(RoomGrid):
    def __init__(self, num_objs):
        super().__init__(
            room_size=16,
            num_rows=2,
            num_cols=2,
            num_objs=num_objs
        )

    def _gen_rooms(self, width, height):
        super()._gen_rooms(width, height)
        names = ['bedroom', 'bathroom', 'kitchen', 'living_room']
        i = 0
        for row in self.room_grid:
            for room in row:
                room.name = names[i]
                i += 1

        # bedroom
        for i in range(5):
            self.grid.horz_wall(0, i, 16)

        # bathroom
        for i in range(16, 23):
            self.grid.horz_wall(0, i, 9)

        for i in range(23, 31):
            self.grid.horz_wall(0, i, 16)

        # kitchen
        for i in range(7):
            self.grid.horz_wall(15, i, 16)
        for i in range(7, 16):
            self.grid.horz_wall(27, i, 4)

    def connect_all(self, door_colors=COLOR_NAMES, max_itrs=5000):
        # down right up left
        bedroom = self.get_room(0, 0)
        bedroom.door_pos[0] = (13, 15)
        bedroom.door_pos[1] = (15, 13)

        kitchen = self.get_room(0, 1)
        kitchen.door_pos[0] = (20, 15)

        bedroom_kitchen = self.add_door(0, 0, 0, self._rand_elem(door_colors), False)
        bedroom_bathroom, _ = self.add_door(0, 0, 1, self._rand_elem(door_colors), False)
        kitchen_livingroom, _ = self.add_door(0, 1, 0, self._rand_elem(door_colors), False)

        return [bedroom_kitchen, bedroom_bathroom, kitchen_livingroom]

    def _gen_objs(self):
        # bedroom
        self.objs['bed'][0].width = 5
        self.objs['bed'][0].height = 7
        self.put_in_room(0, 0, (1, 5), self.objs['bed'][0])

        self.objs['desk'][0].width = 5
        self.objs['desk'][0].height = 3
        self.put_in_room(0, 0, (10, 5), self.objs['desk'][0])

        self.put_in_room(0, 0, (12, 9), self.objs['chair'][0])

        # bathroom
        self.objs['sink'][0].width = 4
        self.put_in_room(0, 1, (9, 6), self.objs['sink'][0])
        self.put_in_room(0, 1, (9, 1, 10), self.objs['toilet'][0])

        # kitchen
        self.objs['counter'][0].width = 8
        self.objs['counter'][0].height = 1
        self.put_in_room(1, 0, (4, 7), self.objs['counter'][0])
        self.objs['counter'][1].width = 1
        self.objs['counter'][1].height = 7
        self.put_in_room(1, 0, (11, 8), self.objs['counter'][1])
        self.put_in_room(1, 0, (1, 7), self.objs['fridge'][0])

        # self.objs['ashcan'][0].width = 1
        # self.objs['ashcan'][0].height = 1
        # self.put_in_room(1, 0, (1, 14), self.objs['ashcan'][0])

        # living room
        self.objs['dining_table'][0].width = 7
        self.objs['dining_table'][0].height = 3
        self.put_in_room(1, 1, (5, 5), self.objs['dining_table'][0])

        self.put_in_room(1, 1, (4, 6), self.objs['chair'][1])
        self.put_in_room(1, 1, (5, 4), self.objs['chair'][2])
        self.put_in_room(1, 1, (7, 4), self.objs['chair'][3])
        self.put_in_room(1, 1, (9, 4), self.objs['chair'][4])
        self.put_in_room(1, 1, (11, 4), self.objs['chair'][5])

        self.put_in_room(1, 1, (12, 6), self.objs['chair'][6])
        self.put_in_room(1, 1, (5, 8), self.objs['chair'][7])
        self.put_in_room(1, 1, (7, 8), self.objs['chair'][8])
        self.put_in_room(1, 1, (9, 8), self.objs['chair'][9])
        self.put_in_room(1, 1, (11, 8), self.objs['chair'][10])

        self.objs['sofa'][0].width = 6
        self.put_in_room(1, 1, (1, 13), self.objs['sofa'][0])
        self.objs['shelving_unit'][0].width = 4
        self.objs['shelving_unit'][0].height = 2
        self.put_in_room(1, 1, (10, 13), self.objs['shelving_unit'][0])

register(
    id='MiniGrid-FixedEnv-32x32-N2-v0',
    entry_point='mini_behavior.mini_behavior.envs:FixedEnv'
)
