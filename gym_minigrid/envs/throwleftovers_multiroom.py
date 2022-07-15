import random
from gym_minigrid.roomgrid import *
from gym_minigrid.register import register


class ThrowLeftoversEnvMulti(RoomGrid):
    """
    Environment in which the agent is instructed to throw away all leftovers into a trash can.
    """

    def __init__(
            self,
            mode='not_human',
            room_size=16,
            num_rows=1,
            num_cols=1,
            max_steps=100,
            num_objs=None
    ):
        if num_objs is None:
            num_objs = {'counter': 4,
                        'plate': 4,
                        'hamburger': 3,
                        'ashcan': 1}

        super().__init__(mode=mode,
                         num_objs=num_objs,
                         room_size=room_size,
                         num_rows=num_rows,
                         num_cols=num_cols,
                         max_steps=max_steps
                         )

    def _gen_grid(self, width, height):
        self._gen_rooms(width, height)

        # return True if not a valid counter space
        def invalid_counter(env, cell):
            x, y = cell
            for i in range(3):
                if env.grid.get(x+i, y) is not None:
                    return True
            return False


        # # generate counter
        # place all objects
        counters = self.objs['counter']
        plates = self.objs['plate']
        hamburgers = self.objs['hamburger']
        ashcans = self.objs['ashcan']

        # place counters
        _, init_counter = self.place_in_room(0, 0, counters[0], reject_fn=invalid_counter)
        for i in range(1, len(counters)):
            x = init_counter[0] + i
            y = init_counter[1]
            self.put_obj(counters[i], x, y)

        # # TODO: generate floor

        # place plates
        for i in range(len(plates)):
            self.put_obj(plates[i], *counters[i].cur_pos)

        # place all hamburgers
        i = 0
        for plate in random.sample(plates, len(hamburgers)):
            self.put_obj(hamburgers[i], *plate.cur_pos)
            i += 1

        # generate ashcan on floor
        for ashcan in ashcans:
            ashcan.on_floor = True
            self.target_pos = self.place_obj(ashcan)

        # check init conditions satisfied
        assert self.init_conditions(), "Does not satisfy initial conditions"

        # randomize the agent start position and orientation
        self.place_agent()
        self.mission = 'throw all {} leftovers in the ashcan'.format(self.num_objs['hamburger'])
        self.connect_all()

    # TODO: automatically generate function from BDDL
    def init_conditions(self):
        assert 'counter' in self.objs.keys(), "No counter"
        assert 'ashcan' in self.objs.keys(), "No ashcan"
        assert 'plate' in self.objs.keys(), "No plates"
        assert 'hamburger' in self.objs.keys(), "No hamburgers"

        for ashcan in self.objs['ashcan']:
            assert ashcan.check_abs_state(self, 'onfloor'), "Ashcan not on floor"

        for plate in self.objs['plate']:
            on_counter = False
            for counter in self.objs['counter']:
                on_counter = plate.check_rel_state(self, counter, 'ontop')
                if on_counter:
                    break
            assert on_counter, "Plate not on counter"

        for hamburger in self.objs['hamburger']:
            on_plate = False
            for plate in self.objs['plate']:
                on_plate = hamburger.check_rel_state(self, plate, 'ontop')
                if on_plate:
                    break
            assert on_plate, "Hamburger not on plate"

        return True

    def step(self, action):
        obs, reward, done, info = super().step(action)

        reward = self._reward()
        done = self._end_condition()

        return obs, reward, done, {}

    def _end_condition(self):
        for hamburger in self.objs['hamburger']:
            is_inside = [hamburger.check_rel_state(self, ashcan, 'inside') for ashcan in self.objs['ashcan']]
            if True not in is_inside:
                return False
        return True

    def _reward(self):
        # fraction of hamburgers thrown away
        num_thrown = 0
        for hamburger in self.objs['hamburger']:
            is_inside = [hamburger.check_rel_state(self, ashcan, 'inside') for ashcan in self.objs['ashcan']]
            if True in is_inside:
                num_thrown += 1

        return num_thrown / self.num_objs['hamburger']


class ThrowLeftoversMulti16x16_Human(ThrowLeftoversEnvMulti):
    def __init__(self):
        super().__init__(mode='human',
                         room_size=16,
                         num_objs={'counter': 4,
                                   'plate': 4,
                                   'hamburger': 3,
                                   'ashcan': 1}
                         )


# non human input env
register(
    id='MiniGrid-ThrowLeftoversMulti-16x16-N2-v0',
    entry_point='gym_minigrid.envs:ThrowLeftoversEnvMulti'
)

# human input env
register(
    id='MiniGrid-ThrowLeftoversMulti-16x16-N2-v1',
    entry_point='gym_minigrid.envs:ThrowLeftoversMulti16x16_Human'
)
