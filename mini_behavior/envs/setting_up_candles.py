from mini_behavior.roomgrid import *
from mini_behavior.register import register


class SettingUpCandlesEnv(RoomGrid):
    """
    Environment in which the agent is instructed to clean a car
    """

    def __init__(
            self,
            mode='primitive',
            room_size=16,
            max_steps=1e5,
    ):
        num_objs = {'candle': 6, 'table': 2, 'box': 2}

        self.mission = 'set up candles'

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=1,
                         num_cols=2,
                         max_steps=max_steps
                         )

    def _gen_objs(self):
        candle = self.objs['candle']
        table = self.objs['table']
        box = self.objs['box']

        self.place_in_room(0, 0, table[0])
        self.place_in_room(1, 0, table[1])

        self.place_in_room(0, 0, box[0])
        self.place_in_room(0, 0, box[1])

        box_pos = self._rand_subset(box[0].all_pos, 3) + self._rand_subset(box[1].all_pos, 3)

        for i in range(6):
            self.put_obj(candle[i], *box_pos[i], 0)

        for obj in candle[:3]:
            obj.states['inside'].set_value(box[0], True)

        for obj in candle[3:]:
            obj.states['inside'].set_value(box[1], True)



    def _end_conditions(self):
        candle = self.objs['candle']
        table = self.objs['table']

        n_0 = 0
        n_1 = 0
        for obj in candle:
            if obj.check_rel_state(self, table[0], 'onTop'):
                n_0 += 1
            elif obj.check_rel_state(self, table[1], 'onTop'):
                n_1 += 1

        return n_0 == 3 and n_1 == 3


# non human input env
register(
    id='MiniGrid-SettingUpCandles-16x16-N2-v0',
    entry_point='mini_behavior.envs:SettingUpCandlesEnv'
)

# human input env
register(
    id='MiniGrid-SettingUpCandles-16x16-N2-v1',
    entry_point='mini_behavior.envs:SettingUpCandlesEnv',
    kwargs={'mode': 'cartesian'}
)
