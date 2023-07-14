from mini_behavior.roomgrid import *
from mini_behavior.register import register


class StoringFoodEnv(RoomGrid):
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
        num_objs = {'oatmeal': 2, 'countertop': 1, 'chip': 2, 'vegetable_oil': 2,
                    'sugar': 2, 'cabinet': 1}

        self.mission = 'store food'

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

    def _gen_objs(self):
        oatmeals = self.objs['oatmeal']
        chips = self.objs['chip']
        countertop = self.objs['countertop'][0]
        vegetable_oils = self.objs['vegetable_oil']
        sugars = self.objs['sugar']
        cabinet = self.objs['cabinet'][0]

        countertop.width, countertop.height = 4, 3

        self.place_obj(countertop)
        self.place_obj(cabinet)

        countertop_pos = self._rand_subset(countertop.all_pos, 8)
        self.put_obj(oatmeals[0], *countertop_pos[0], 1)
        self.put_obj(oatmeals[1], *countertop_pos[1], 1)
        self.put_obj(chips[0], *countertop_pos[2], 1)
        self.put_obj(chips[1], *countertop_pos[3], 1)
        self.put_obj(vegetable_oils[0], *countertop_pos[4], 1)
        self.put_obj(vegetable_oils[1], *countertop_pos[5], 1)
        self.put_obj(sugars[0], *countertop_pos[6], 1)
        self.put_obj(sugars[1], *countertop_pos[7], 1)



    def _end_conditions(self):
        oatmeals = self.objs['oatmeal']
        chips = self.objs['chip']
        vegetable_oils = self.objs['vegetable_oil']
        sugars = self.objs['sugar']
        cabinet = self.objs['cabinet'][0]

        for obj in oatmeals + chips + vegetable_oils + sugars:
            if not obj.check_rel_state(self, cabinet, 'inside'):
                return False

        return True


# non human input env
register(
    id='MiniGrid-StoringFood-16x16-N2-v0',
    entry_point='mini_behavior.envs:StoringFoodEnv'
)

# human input env
register(
    id='MiniGrid-StoringFood-16x16-N2-v1',
    entry_point='mini_behavior.envs:StoringFoodEnv',
    kwargs={'mode': 'cartesian'}
)
