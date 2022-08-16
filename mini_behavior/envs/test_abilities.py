from mini_behavior.roomgrid import *
from mini_behavior.register import register


class TestAbilitiesEnv(RoomGrid):
    """
    init:
    - bin = dusty and stained
    - fridge = off

    0. pickup towel
    1. clean bin with towel (towel not soaked) -- bin should not be dusty
    2. put towel at sink when sink off -- towel should not be soaked
    3. toggle on sink
    4. towel should be soaked
    5. clean bin with towel (towel soaked) -- bin should not be stained
    7. put strawberry in fridge -- strawberry should be frozen
    9. take out strawberry -- strawberry should not be frozen
    10. pickup knife
    11. slice strawberry -- strawberry should be sliced
    12. navigate to stove and toggle on -- strawberry should not be able to be cooked
    13. pickup pan
    14. navigate to stove and cook strawberry -- strawberry should be cooked
    """

    def __init__(
            self,
            num_rows=1,
            num_cols=1,
    ):
        num_objs = {'beef': 1, # freezable, red
                    'bin': 1, # dustyable, stainable, purple
                    'towel': 1, # soakable, stainable, cleaningtool, white
                    'sink': 1, # waterSource, yellow
                    'electric_refrigerator': 1, # coldsource, blue,
                    'stove': 1,
                    'knife': 1,
                    'pan': 1
                    }

        super().__init__(mode='human',
                         num_objs=num_objs,
                         room_size=16,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=1e5
                         )

        bin = self.objs['bin'][0]
        bin.states['dustyable'].set_value(True)
        bin.states['stainable'].set_value(True)

        for obj in self.obj_instances.values():
            for name, state in obj.states.items():
                if state.type == 'absolute':
                    print(f'{obj.name} {name}: {state.get_value(self)}')

    def _gen_grid(self, width, height):
        self._gen_rooms(width, height)

        # generate other objects
        for obj in self.obj_instances.values():
            self.place_in_room(0, 0, obj, reject_fn=None)

        # randomize the agent start position and orientation
        self.place_agent()
        self.mission = 'place cooked beef in the refrigerator'
        self.connect_all()

    def _end_conditions(self):
        return False

    def _reward(self):
        return 0


# human control env
register(
    id='MiniGrid-TestAbilities-16x16-N1-v0',
    entry_point='mini_behavior.envs:TestAbilitiesEnv'
)

