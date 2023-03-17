# FROM MINIGRID REPO
from mini_behavior.roomgrid import *
from mini_behavior.register import register


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
        # Create the grid
        # self.grid = BehaviorGrid(width, height)
        self.room_grid = []  # list of lists
        self.doors = []

        # For each row of rooms
        for j in range(0, self.num_rows):
            row = []

            # For each column of rooms
            for i in range(0, self.num_cols):
                room = Room(
                    top=(i * (self.room_size - 1), j * (self.room_size - 1)),
                    size=(self.room_size, self.room_size),
                    row=j,
                    col=i
                )
                row.append(room)

                # Generate the walls for this room
                # self.grid.wall_rect(*room.top, *room.size)

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
                    room.neighbors[0] = self.room_grid[j][i + 1]
                    room.door_pos[0] = (x_m, self._rand_int(y_l, y_m))
                if j < self.num_rows - 1:
                    room.neighbors[1] = self.room_grid[j + 1][i]
                    room.door_pos[1] = (self._rand_int(x_l, x_m), y_m)
                if i > 0:
                    room.neighbors[2] = self.room_grid[j][i - 1]
                    room.door_pos[2] = room.neighbors[2].door_pos[0]
                if j > 0:
                    room.neighbors[3] = self.room_grid[j - 1][i]
                    room.door_pos[3] = room.neighbors[3].door_pos[1]

        names = ['bedroom', 'bathroom', 'kitchen', 'living_room']
        i = 0
        for row in self.room_grid:
            for room in row:
                room.name = names[i]
                i += 1


        # bedroom
        for i in range(4):
            self.grid.horz_wall(0, i, 16, color='white')
        self.grid.horz_wall(0, 4, 16, color='grey')

        # bathroom
        self.grid.horz_wall(0, 15, 31, color='grey')
        self.grid.vert_wall(0, 4, 12, color='grey')
        self.grid.vert_wall(15, 4, 27, color='grey')
        self.grid.vert_wall(30, 15, 15, color='grey')
        self.grid.horz_wall(15, 30, 16, color='grey')

        for i in range(16, 24):
            self.grid.horz_wall(0, i, 8, color='white')
        self.grid.vert_wall(8, 16, 7, color='grey')

        self.grid.horz_wall(8, 23, 8, color='grey')
        for i in range(24, 31):
            self.grid.horz_wall(0, i, 16, color='white')

        # kitchen
        self.grid.horz_wall(15, 6, 13, color='grey')
        for i in range(6):
            self.grid.horz_wall(15, i, 16, color='white')

        self.grid.vert_wall(27, 7, 9, color='grey')
        for i in range(6, 16):
            self.grid.horz_wall(28, i, 3, color='white')

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
        self.put_in_room(0, 0, (2, 6), self.objs['bed'][0])

        self.objs['desk'][0].width = 5
        self.objs['desk'][0].height = 3
        self.put_in_room(0, 0, (9, 6), self.objs['desk'][0])

        self.put_in_room(0, 0, (12, 10), self.objs['chair'][0])

        # bathroom
        self.objs['sink'][0].width = 4
        self.put_in_room(0, 1, (9, 5), self.objs['sink'][0])
        self.objs['toilet'][0].width = 1
        self.objs['toilet'][0].height = 1
        self.put_in_room(0, 1, (9, 1, 10), self.objs['toilet'][0])

        # kitchen
        self.objs['counter_top'][0].width = 8
        self.objs['counter_top'][0].height = 1
        self.put_in_room(1, 0, (4, 7), self.objs['counter_top'][0])
        self.objs['counter_top'][1].width = 1
        self.objs['counter_top'][1].height = 7
        self.put_in_room(1, 0, (11, 8), self.objs['counter_top'][1])
        self.objs['fridge'][0].width = 2
        self.objs['fridge'][0].height = 2
        self.put_in_room(1, 0, (1, 8), self.objs['fridge'][0])

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
        self.objs['sofa'][0].height = 1
        self.put_in_room(1, 1, (1, 14), self.objs['sofa'][0])
        self.objs['shelving_unit'][0].width = 4
        self.objs['shelving_unit'][0].height = 1
        self.put_in_room(1, 1, (10, 14), self.objs['shelving_unit'][0])

register(
    id='MiniGrid-FixedEnv-32x32-N2-v0',
    entry_point='mini_behavior.mini_behavior.envs:FixedEnv'
)
