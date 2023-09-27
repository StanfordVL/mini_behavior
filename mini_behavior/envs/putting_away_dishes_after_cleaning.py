from mini_behavior.roomgrid import *
from mini_behavior.register import register


class PuttingAwayDishesAfterCleaningEnv(RoomGrid):
    """
    Environment in which the agent is instructed to put away dishes after cleaning
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
        num_objs = {'plate': 8, 'countertop': 2, 'cabinet': 1}

        self.mission = 'put away dishes after cleaning'

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps,
                         dense_reward=dense_reward,
                         )

    def _gen_objs(self):
        plate = self.objs['plate']
        countertop = self.objs['countertop']
        cabinet = self.objs['cabinet'][0]

        self.place_obj(countertop[0])
        self.place_obj(countertop[1])
        self.place_obj(cabinet)

        countertop_pos = self._rand_subset(countertop[0].all_pos, 4) + self._rand_subset(countertop[1].all_pos, 4)

        for i in range(8):
            self.put_obj(plate[i], *countertop_pos[i], 1)

    def _end_conditions(self):
        plate = self.objs['plate']
        cabinet = self.objs['cabinet'][0]

        for obj in plate:
            if not obj.check_rel_state(self, cabinet, 'inside'):
                return False

        return True

    # This score measures progress towards the goal
    def get_progress(self):
        plate = self.objs['plate']
        cabinet = self.objs['cabinet'][0]
        score = 0
        for obj in plate:
            if obj.check_rel_state(self, cabinet, 'inside'):
                score += 1
        if cabinet.check_abs_state(self, 'openable'):
            score += 1

        return score


# non human input env
register(
    id='MiniGrid-PuttingAwayDishesAfterCleaning-16x16-N2-v0',
    entry_point='mini_behavior.envs:PuttingAwayDishesAfterCleaningEnv'
)

# non human input env
register(
    id='MiniGrid-PuttingAwayDishesAfterCleaningDense-10x10-N2-v0',
    entry_point='mini_behavior.envs:PuttingAwayDishesAfterCleaningEnv',
    kwargs={'room_size': 10, 'max_steps': 1000, 'dense_reward': True}
)

# human input env
register(
    id='MiniGrid-PuttingAwayDishesAfterCleaning-16x16-N2-v1',
    entry_point='mini_behavior.envs:PuttingAwayDishesAfterCleaningEnv',
    kwargs={'mode': 'cartesian'}
)
