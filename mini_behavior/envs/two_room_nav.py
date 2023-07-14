from mini_behavior.roomgrid import *
from mini_behavior.register import register


class TwoRoomNavigationEnv(RoomGrid):
    """
    Environment in which the agent is instructed to navigate to a target position
    """

    # Enumeration of possible actions
    class Actions(IntEnum):
        # Turn left, turn right, move forward
        left = 0
        right = 1
        forward = 2

    def __init__(
            self,
            max_steps=1e5,
    ):
        super().__init__(mode='cartesian',
                         num_objs={'ball': 1},
                         room_size=8,
                         num_rows=1,
                         num_cols=2,
                         max_steps=max_steps,
                         see_through_walls=True,
                         agent_view_size=3,
                         highlight=False
                         )

    def _gen_grid(self, width, height):
        self._gen_rooms(width, height)
        # randomize the agent start position and orientation
        self._gen_objs()
        self.place_agent()
        self.connect_all()
        self.mission = 'navigate between rooms'

    def _gen_objs(self):
        for obj in self.obj_instances.values():
            self.place_obj(obj)

    def _end_conditions(self):
        return False


register(
    id='MiniGrid-TwoRoomNavigation-8x8-N2-v0',
    entry_point='mini_behavior.envs:TwoRoomNavigationEnv'
)
