from mini_behavior.roomgrid import *
from mini_behavior.register import register


class WateringHouseplantsEnv(RoomGrid):
    """
    Environment in which the agent is instructed to clean a car
    """

    def __init__(
            self,
            mode='primitive',
            room_size=16,
            max_steps=1e5,
    ):
        num_objs = {'pot_plant': 3, 'sink': 1, 'table': 1, 'countertop': 1}

        self.mission = 'water houseplants'

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=1,
                         num_cols=2,
                         max_steps=max_steps
                         )

    def _gen_objs(self):
        pot_plants = self.objs['pot_plant']
        sink = self.objs['sink'][0]
        table = self.objs['table'][0]
        countertop = self.objs['countertop'][0]

        self.place_in_room(0, 0, table)
        self.place_in_room(1, 0, countertop)
        self.place_in_room(1, 0, sink)

        self.place_in_room(0, 0, pot_plants[0])
        self.place_in_room(0, 0, pot_plants[1])
        self.place_in_room(1, 0, pot_plants[2])

        for plant in pot_plants:
            plant.states['soakable'].set_value(False)

        # TODO: agent start in room 2



    def _end_conditions(self):
        pot_plants = self.objs['pot_plant']

        for plant in pot_plants:
            if not plant.check_abs_state(self, 'soakable'):
                return False

        return True


# non human input env
register(
    id='MiniGrid-WateringHouseplants-16x16-N2-v0',
    entry_point='mini_behavior.envs:WateringHouseplantsEnv'
)

# human input env
register(
    id='MiniGrid-WateringHouseplants-16x16-N2-v1',
    entry_point='mini_behavior.envs:WateringHouseplantsEnv',
    kwargs={'mode': 'cartesian'}
)
