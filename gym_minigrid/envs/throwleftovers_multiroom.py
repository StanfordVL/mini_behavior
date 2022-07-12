import random
from gym_minigrid.utils import *
from gym_minigrid.roomgrid import *
from gym_minigrid.register import register


class ThrowLeftoversEnvMulti(RoomGrid):
    """
    Environment in which the agent is instructed to throw away all leftovers into a trash can.
    """

    def __init__(
            self,
            room_size=16,
            num_rows=1,
            num_cols=1,
            max_steps=1e5,
            num_plates=4,
            num_hamburgers=3,
    ):
        self.num_plates = num_plates
        self.num_hamburgers = num_hamburgers

        self.objs = {}
        self.num_thrown = 0

        super().__init__(room_size=room_size,
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

        def init_conditions():
            assert 'counters' in self.objs.keys(), "No counter"
            assert 'ashcan' in self.objs.keys(), "No ashcan"
            assert 'plates' in self.objs.keys(), "No plates"
            assert 'hamburgers' in self.objs.keys(), "No hamburgers"

            for ashcan in self.objs['ashcan']:
                assert ashcan.check_abs_state(self, 'onfloor'), "Ashcan not on floor"

            for plate in self.objs['plates']:
                on_counter = False
                for counter in self.objs['counters']:
                    on_counter = plate.check_rel_state(self, counter, 'ontop')
                    if on_counter:
                        break
                assert on_counter, "Plate not on counter"

            for hamburger in self.objs['hamburgers']:
                on_plate = False
                for plate in self.objs['plates']:
                    on_plate = hamburger.check_rel_state(self, plate, 'ontop')
                    if on_plate:
                        break
                assert on_plate, "Hamburger not on plate"

        # # generate counter
        counters = [Counter('purple', 'counter_0')]
        _, init_counter = self.place_in_room(0, 0, counters[0], reject_fn=invalid_counter)
        for i in range(1, self.num_plates):
            counter = Counter('purple', 'counter_{}'.format(i))
            x = init_counter[0] + i
            y = init_counter[1]
            self.put_obj(counter, x, y)
            counters.append(counter)
        self.objs['counters'] = counters

        # # TODO: generate floor
        #
        # generate all plates
        plates = []
        i = 0
        for counter in counters:
            plate = Ball('yellow', 'plate_{}'.format(i))
            self.put_obj(plate, *counter.cur_pos)
            plates.append(plate)
            i += 1
        self.objs['plates'] = plates

        # generate all hamburgers
        hamburgers = []
        i = 0
        for plate in random.sample(plates, self.num_hamburgers):
            hamburger = S_ball('red', 'hamburger_{}'.format(i))
            self.put_obj(hamburger, *plate.cur_pos)
            hamburgers.append(hamburger)
            i += 1
        self.objs['hamburgers'] = hamburgers

        # generate ashcan on floor
        ashcan = Ashcan('green', 'ashcan_0')
        ashcan.on_floor = True
        self.objs['ashcan'] = [ashcan]
        self.target_pos = self.place_obj(self.objs['ashcan'][0])

        # check init conditions satisfied
        init_conditions()

        # randomize the agent start position and orientation
        self.place_agent()
        self.mission = 'throw all {} leftovers in the ashcan'.format(self.num_hamburgers)
        self.connect_all()

    def step(self, action):
        obs, reward, done, info = super().step(action)
        # obj = self.agent_object
        #
        # # if dropping an object
        # if action == self.actions.drop and obj:
        #     # if dropped a hamburger into the ashcan
        #     pos = [obj.check_rel_state(self, ashcan, 'inside') for ashcan in self.objs['ashcan']]
        #     if obj in self.objs['hamburgers'] and True in pos:
        #         # TODO: set reward
        #         # reward = self._reward()
        #         self.num_thrown += 1
        #         print('Num remaining hamburgers: ' + str(self.num_hamburgers - self.num_thrown))

        # done if succesfully throw away all leftovers
        def end_condition():
            for hamburger in self.objs['hamburgers']:
                is_inside = [hamburger.check_rel_state(self, ashcan, 'inside') for ashcan in self.objs['ashcan']]
                if True not in is_inside:
                    return False
            return True

        done = end_condition()

        return obs, reward, done, {}

    def _reward(self):
        return


class ThrowLeftoversMulti16x16N3(ThrowLeftoversEnvMulti):
    def __init__(self):
        super().__init__(grid_size=32, num_plates=4, num_hamburgers=3)


register(
    id='MiniGrid-ThrowLeftoversMulti-16x16-N2-v0',
    entry_point='gym_minigrid.envs:ThrowLeftoversEnvMulti'
)    

register(        
    id='MiniGrid-ThrowLeftoversMulti-32x32-N3-v0',
    entry_point='gym_minigrid.envs:ThrowLeftoversMulti32x32N3'
)


