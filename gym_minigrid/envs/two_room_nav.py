from gym_minigrid.roomgrid import *
from gym_minigrid.register import register


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
        super().__init__(mode='human',
                         num_objs={},
                         room_size=8,
                         num_rows=2,
                         num_cols=1,
                         max_steps=max_steps,
                         see_through_walls=True,
                         agent_view_size=3,
                         highlight=False
                         )

    def _gen_grid(self, width, height):
        self._gen_rooms(width, height)

        # generate goal position
        # goal = self.objs['goal'][0]
        # _, self.target_pos = self.place_in_room(0, 0, goal, reject_fn=None)

        # randomize the agent start position and orientation
        self.place_agent()
        self.mission = 'navigate between rooms'
        self.connect_all()

    def _end_conditions(self):
        # if np.all(self.agent.cur_pos == self.target_pos):
        #     return True
        # else:
        #     return False
        return False

    def _reward(self):
        if self._end_conditions():
            return 1
        else:
            return 0


register(
    id='MiniGrid-TwoRoomNavigation-8x8-N2-v0',
    entry_point='gym_minigrid.envs:TwoRoomNavigationEnv'
)
