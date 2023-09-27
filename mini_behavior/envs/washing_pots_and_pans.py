from mini_behavior.roomgrid import *
from mini_behavior.register import register


class WashingPotsAndPansEnv(RoomGrid):
    """
    Environment in which the agent is instructed to wash pots and pans
    """

    def __init__(
            self,
            mode='primitive',
            room_size=16,
            num_rows=1,
            num_cols=1,
            max_steps=1e5,
            dense_reward=False,
    ):
        num_objs = {'teapot': 1, 'kettle': 1, 'pan': 3, 'countertop': 2, 'sink': 1, 'scrub_brush': 1, 'soap': 1, 'cabinet': 2}

        self.mission = 'wash pots and pans'

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps,
                         dense_reward=dense_reward,
                         )

    def _gen_objs(self):
        teapot = self.objs['teapot'][0]
        kettle = self.objs['kettle'][0]
        pans = self.objs['pan']
        countertops = self.objs['countertop']
        sink = self.objs['sink'][0]
        scrub_brush = self.objs['scrub_brush'][0]
        soap = self.objs['soap'][0]
        cabinets = self.objs['cabinet']

        self.place_obj(countertops[0])
        self.place_obj(countertops[1])
        self.place_obj(cabinets[0])
        self.place_obj(cabinets[1])
        self.place_obj(sink)

        countertop_0_pos = self._rand_subset(countertops[0].all_pos, 3)
        countertop_1_pos = self._rand_subset(countertops[1].all_pos, 3)

        self.put_obj(teapot, *countertop_0_pos[0], 1)
        teapot.states['stainable'].set_value(True)
        self.put_obj(kettle, *countertop_1_pos[0], 1)
        kettle.states['stainable'].set_value(True)
        self.put_obj(pans[0], *countertop_0_pos[1], 1)
        pans[0].states['stainable'].set_value(True)
        self.put_obj(pans[1], *countertop_0_pos[2], 1)
        pans[1].states['stainable'].set_value(True)
        self.put_obj(pans[2], *countertop_1_pos[1], 1)
        pans[2].states['stainable'].set_value(True)

        self.put_obj(scrub_brush, *countertop_1_pos[2], 1)
        scrub_brush.states['soakable'].set_value(True)

        self.put_obj(soap, *sink.cur_pos, 0)
        soap.states['inside'].set_value(sink, True)

    def _end_conditions(self):
        teapots = self.objs['teapot']
        kettles = self.objs['kettle']
        pans = self.objs['pan']

        for obj in pans + kettles + teapots:
            if obj.check_abs_state(self, 'stainable'):
                return False

            if obj.inside_of is None or type(obj.inside_of) != Cabinet:
                return False

        return True

    # This score measures progress towards the goal
    def get_progress(self):
        teapots = self.objs['teapot']
        kettles = self.objs['kettle']
        pans = self.objs['pan']

        score = 0
        for obj in pans + kettles + teapots:
            if not obj.check_abs_state(self, 'stainable'):
                score += 1

            if obj.inside_of is not None and type(obj.inside_of) == Cabinet:
                score += 1

        for cab in self.objs['cabinet']:
            if cab.check_abs_state(self, 'openable'):
                score += 1

        return score


# non human input env
register(
    id='MiniGrid-WashingPotsAndPans-16x16-N2-v0',
    entry_point='mini_behavior.envs:WashingPotsAndPansEnv'
)

# non human input env
register(
    id='MiniGrid-WashingPotsAndPansDense-10x10-N2-v0',
    entry_point='mini_behavior.envs:WashingPotsAndPansEnv',
    kwargs={'room_size': 10, 'max_steps': 1000, 'dense_reward': True}
)

# human input env
register(
    id='MiniGrid-WashingPotsAndPans-16x16-N2-v1',
    entry_point='mini_behavior.envs:WashingPotsAndPansEnv',
    kwargs={'mode': 'cartesian'}
)
