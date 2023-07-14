from mini_behavior.roomgrid import *
from mini_behavior.register import register


class MakingTeaEnv(RoomGrid):
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
        num_objs = {'teapot': 1, 'tea_bag': 1, 'lemon': 1, 'knife': 1, 'cabinet': 1, 'electric_refrigerator': 1, 'stove': 1}

        self.mission = 'make tea'

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

    def _gen_objs(self):
        teapot = self.objs['teapot'][0]
        tea_bag = self.objs['tea_bag'][0]
        lemon = self.objs['lemon'][0]
        knife = self.objs['knife'][0]
        cabinet = self.objs['cabinet'][0]
        electric_refrigerator = self.objs['electric_refrigerator'][0]
        stove = self.objs['stove'][0]

        self.place_obj(cabinet)
        self.place_obj(electric_refrigerator)
        self.place_obj(stove)

        # place teapot, tea_bag, knife in cabinet
        pos_1, pos_2, pos_3 = self._rand_subset(cabinet.all_pos, 3)
        self.put_obj(teapot, *pos_1, 1)
        self.put_obj(tea_bag, *pos_2, 0)
        self.put_obj(knife, *pos_3, 0)

        for obj in [teapot, tea_bag, knife]:
            obj.states['inside'].set_value(cabinet, 'inside')

        # place lemon in fridge
        pos = self._rand_subset(electric_refrigerator.all_pos, 1)[0]
        self.put_obj(lemon, *pos, 1)
        lemon.states['inside'].set_value(electric_refrigerator, 'inside')

    def _init_conditions(self):
        for obj_type in ['teapot', 'tea_bag', 'lemon', 'knife', 'cabinet', 'electric_refrigerator', 'stove']:
            assert obj_type in self.objs.keys(), f"No {obj_type}"

        teapot = self.objs['teapot'][0]
        tea_bag = self.objs['tea_bag'][0]
        lemon = self.objs['lemon'][0]
        knife = self.objs['knife'][0]
        cabinet = self.objs['cabinet'][0]
        electric_refrigerator = self.objs['electric_refrigerator'][0]

        assert teapot.check_rel_state(self, cabinet, 'inside')
        assert tea_bag.check_rel_state(self, cabinet, 'inside')
        assert knife.check_rel_state(self, cabinet, 'inside')

        assert lemon.check_rel_state(self, electric_refrigerator, 'inside')

        return True



    def _end_conditions(self):
        teapot = self.objs['teapot'][0]
        tea_bag = self.objs['tea_bag'][0]
        lemon = self.objs['lemon'][0]
        stove = self.objs['stove'][0]

        if lemon.check_abs_state(self, 'sliceable') and \
                teapot.check_rel_state(self, stove, 'onTop') and \
                tea_bag.check_rel_state(self, teapot, 'atsamelocation') and \
                tea_bag.check_abs_state(self, 'soakable') and \
                stove.check_abs_state(self, 'toggleable'):
            return True

        return False


# non human input env
register(
    id='MiniGrid-MakingTea-16x16-N2-v0',
    entry_point='mini_behavior.envs:MakingTeaEnv'
)

# human input env
register(
    id='MiniGrid-MakingTea-16x16-N2-v1',
    entry_point='mini_behavior.envs:MakingTeaEnv',
    kwargs={'mode': 'cartesian'}
)
