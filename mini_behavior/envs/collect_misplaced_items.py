from mini_behavior.roomgrid import *
from mini_behavior.register import register


class CollectMisplacedItemsEnv(RoomGrid):
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
        num_objs = {'gym_shoe': 1, 'necklace': 1, 'notebook': 1, 'sock': 2, 'table': 2, 'cabinet': 1, 'sofa': 1}

        self.mission = 'collect misplaced items onto a table'

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

    def _gen_objs(self):
        gym_shoe = self.objs['gym_shoe'][0]
        necklace = self.objs['necklace'][0]
        notebook = self.objs['notebook'][0]
        cabinet = self.objs['cabinet'][0]
        sofa = self.objs['sofa'][0]

        socks = self.objs['sock']
        tables = self.objs['table']

        self.place_obj(tables[0])
        self.place_obj(tables[1])
        self.place_obj(necklace)
        self.place_obj(cabinet)

        table_0_pos = self._rand_subset(tables[0].all_pos, 1)[0]
        self.put_obj(gym_shoe, *table_0_pos, 0)

        cabinet_pos = self._rand_subset(cabinet.all_pos, 1)[0]
        self.put_obj(gym_shoe, *cabinet_pos, 2)

        table_1_pos = self._rand_subset(tables[1].all_pos, 2)[0]
        self.put_obj(notebook, *table_1_pos, 0)

        self.place_obj(sofa)
        self.put_obj(socks[0], *self._rand_elem(sofa.all_pos), 1)
        self.place_obj(socks[1])

    def _init_conditions(self):
        for obj_type in ['gym_shoe', 'necklace', 'notebook', 'sock', 'table', 'cabinet', 'sofa']:
            assert obj_type in self.objs.keys(), f"No {obj_type}"

        return True



    def _end_conditions(self):
        gym_shoe = self.objs['gym_shoe']
        necklace = self.objs['necklace']
        notebook = self.objs['notebook']

        socks = self.objs['sock']
        tables = self.objs['table']

        for obj in gym_shoe + necklace + notebook + socks:
            if not obj.check_rel_state(self, tables[1], 'onTop'):
                return False

        return True


# non human input env
register(
    id='MiniGrid-CollectMisplacedItems-16x16-N2-v0',
    entry_point='mini_behavior.envs:CollectMisplacedItemsEnv'
)

# human input env
register(
    id='MiniGrid-CollectMisplacedItems-16x16-N2-v1',
    entry_point='mini_behavior.envs:CollectMisplacedItemsEnv',
    kwargs={'mode': 'cartesian'}
)
