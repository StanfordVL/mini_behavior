from gym_minigrid.roomgrid import *
from gym_minigrid.register import register
from gym_minigrid.bddl import _CONTROLS


class NavigationEnv(RoomGrid):
    """
    Environment in which the agent is instructed to navigate to a target position
    """

    def __init__(
            self,
            mode='not_human',
            room_size=16,
            num_rows=1,
            num_cols=1,
            max_steps=1e5,
            num_objs=None
    ):
        if num_objs is None:
            num_objs = {'goal': 1}

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

    def _gen_grid(self, width, height):
        self._gen_rooms(width, height)

        # generate goal position
        goal = self.objs['goal'][0]
        _, self.target_pos = self.place_in_room(0, 0, goal, reject_fn=None)
        goal.on_floor = True

        # generate other objects
        if 'ball' in self.objs.keys():
            balls = self.objs['ball']
            for ball in balls:
                self.place_in_room(0, 0, ball, reject_fn=None)

        # randomize the agent start position and orientation
        self.place_agent()
        self.mission = 'navigate to the target position'
        self.connect_all()

    def step(self, action):
        obs, reward, done, info = super().step(action)

        reward = self._reward()
        done = self._end_condition()

        return obs, reward, done, {}

    def _end_condition(self):
        if np.all(self.agent.cur_pos == self.target_pos):
            return True
        else:
            return False

    def _reward(self):
        if self._end_condition():
            return 1
        else:
            return 0


class NavigationEnv16x16_Human(NavigationEnv):
    def __init__(self):
        super().__init__(mode='human',
                         room_size=16,
                         )


class NavigationEnv16x16_RL(NavigationEnv):
    def __init__(self):
        super().__init__(mode='not_human',
                         room_size=16,
                         )

class NavigationEnv8x8_Human(NavigationEnv):
    def __init__(self):
        super().__init__(mode='human',
                         room_size=8,
                         )


class NavigationEnv8x8_RL(NavigationEnv):
    def __init__(self):
        super().__init__(mode='not_human',
                         room_size=8,
                         )


class NavigationMultiEnv16x16_Human(NavigationEnv):
    def __init__(self):
        super().__init__(mode='human',
                         room_size=16,
                         num_rows=2,
                         num_cols=2
                         )


class NavigationMultiEnv16x16_RL(NavigationEnv):
    def __init__(self):
        super().__init__(mode='not_human',
                         room_size=16,
                         num_rows=2,
                         num_cols=2
                         )

class NavigationMultiEnv8x8_Human(NavigationEnv):
    def __init__(self):
        super().__init__(mode='human',
                         room_size=8,
                         num_rows=2,
                         num_cols=2
                         )


class NavigationMultiEnv8x8_RL(NavigationEnv):
    def __init__(self):
        super().__init__(mode='not_human',
                         room_size=8,
                         num_rows=2,
                         num_cols=2
                         )


class NavigationObjEnv16x16_Human(NavigationEnv):
    def __init__(self):
        super().__init__(mode='human',
                         room_size=16,
                         num_objs={'goal': 1,
                                   'ball': 4
                                   }
                         )


class NavigationObjEnv16x16_RL(NavigationEnv):
    def __init__(self):
        super().__init__(mode='not_human',
                         room_size=16,
                         num_objs={'goal': 1,
                                   'ball': 4
                                   }
                         )

# human control env
register(
    id='MiniGrid-Navigation-16x16-N1-v0',
    entry_point='gym_minigrid.envs:NavigationEnv16x16_Human'
)

# RL agent env
register(
    id='MiniGrid-Navigation-16x16-N2-v0',
    entry_point='gym_minigrid.envs:NavigationEnv16x16_RL'
)

# human control env
register(
    id='MiniGrid-Navigation-8x8-N1-v0',
    entry_point='gym_minigrid.envs:NavigationEnv8x8_Human'
)

# RL agent env
register(
    id='MiniGrid-Navigation-8x8-N2-v0',
    entry_point='gym_minigrid.envs:NavigationEnv8x8_RL'
)

##### MULTI ROOM
# human control env
register(
    id='MiniGrid-NavigationMulti-16x16-N1-v0',
    entry_point='gym_minigrid.envs:NavigatioMultiEnv16x16_Human'
)

# RL agent env
register(
    id='MiniGrid-NavigationMulti-16x16-N2-v0',
    entry_point='gym_minigrid.envs:NavigatioMultiEnv16x16_RL'
)

# human control env
register(
    id='MiniGrid-NavigationMulti-8x8-N1-v0',
    entry_point='gym_minigrid.envs:NavigatioMultiEnv8x8_Human'
)

# RL agent env
register(
    id='MiniGrid-NavigationMulti-8x8-N2-v0',
    entry_point='gym_minigrid.envs:NavigationMultiEnv8x8_RL'
)


##### OBJECTS
# human control env
register(
    id='MiniGrid-NavigationObj-16x16-N1-v0',
    entry_point='gym_minigrid.envs:NavigationObjEnv16x16_Human'
)

# RL agent env
register(
    id='MiniGrid-NavigationObj-16x16-N2-v0',
    entry_point='gym_minigrid.envs:NavigationObjEnv16x16_RL'
)
