from mini_behavior.roomgrid import *
from mini_behavior.register import register


class SortingBooksEnv(RoomGrid):
    """
    Environment in which the agent is instructed to clean a car
    """

    def __init__(
            self,
            mode='primitive',
            room_size=16,
            num_rows=1,
            num_cols=1,
            max_steps=1e5,
    ):
        num_objs = {'book': 2, 'hardback': 2, 'table': 1, 'shelf': 1}

        self.mission = 'sort books'

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

    def _gen_objs(self):
        book = self.objs['book']
        hardback = self.objs['hardback']
        table = self.objs['table'][0]
        shelf = self.objs['shelf'][0]

        self.place_obj(table)
        self.place_obj(shelf)
        self.place_obj(book[0])
        self.place_obj(hardback[0])

        table_pos = self._rand_subset(table.all_pos, 2)
        self.put_obj(book[1], *table_pos[0], 2)
        self.put_obj(hardback[1], *table_pos[1], 2)



    def _end_conditions(self):
        book = self.objs['book']
        hardback = self.objs['hardback']
        shelf = self.objs['shelf'][0]

        for obj in book + hardback:
            if not obj.check_rel_state(self, shelf, 'onTop'):
                return False

        return True


# non human input env
register(
    id='MiniGrid-SortingBooks-16x16-N2-v0',
    entry_point='mini_behavior.envs:SortingBooksEnv'
)

# human input env
register(
    id='MiniGrid-SortingBooks-16x16-N2-v1',
    entry_point='mini_behavior.envs:SortingBooksEnv',
    kwargs={'mode': 'cartesian'}
)
