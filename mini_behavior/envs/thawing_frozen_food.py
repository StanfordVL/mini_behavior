from mini_behavior.roomgrid import *
from mini_behavior.register import register


class ThawingFrozenFoodEnv(RoomGrid):
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
        num_objs = {'date': 1, 'electric_refrigerator': 1, 'olive': 1, 'fish': 4, 'sink': 1}

        self.mission = 'thaw frozen food'

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

    def _gen_objs(self):
        date = self.objs['date']
        olive = self.objs['olive']
        fish = self.objs['fish']
        electric_refrigerator = self.objs['electric_refrigerator'][0]
        sink = self.objs['sink'][0]

        self.place_obj(electric_refrigerator)
        self.place_obj(sink)

        fridge_pos = self._rand_subset(electric_refrigerator.all_pos, 4)
        self.put_obj(date[0], *fridge_pos[0], 1)
        self.put_obj(olive[0], *fridge_pos[1], 1)
        self.put_obj(fish[0], *fridge_pos[2], 2)
        self.put_obj(fish[1], *fridge_pos[3], 1)
        self.put_obj(fish[2], *fridge_pos[0], 0)
        self.put_obj(fish[3], *fridge_pos[2], 2)

        for obj in date + olive + fish:
            obj.states['inside'].set_value(electric_refrigerator, True)



    def _init_conditions(self):
        for obj in self.objs['date'] + self.objs['olive'] + self.objs['fish']:
            assert obj.check_abs_state(self, 'freezable')

    def _end_conditions(self):
        date = self.objs['date'][0]
        olive = self.objs['olive'][0]
        fishes = self.objs['fish']
        sink = self.objs['sink'][0]

        nextto = False
        for fish in fishes:
            if date.check_rel_state(self, fish, 'nextto'):
                nextto = True

        if not nextto:
            return False

        for fish in fishes:
            if not fish.check_rel_state(self, sink, 'nextto'):
                return False

        if not olive.check_rel_state(self, sink, 'nextto'):
            return False

        return True


# non human input env
register(
    id='MiniGrid-ThawingFrozenFood-16x16-N2-v0',
    entry_point='mini_behavior.envs:ThawingFrozenFoodEnv'
)

# human input env
register(
    id='MiniGrid-ThawingFrozenFood-16x16-N2-v1',
    entry_point='mini_behavior.envs:ThawingFrozenFoodEnv',
    kwargs={'mode': 'cartesian'}
)
