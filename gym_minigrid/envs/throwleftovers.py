import random
from gym_minigrid.minigrid import *
from gym_minigrid.register import register


class ThrowLeftoversEnv(MiniGridEnv):
    """
    Environment in which the agent is instructed to throw away all leftovers into a trash can.
    """

    def __init__(
            self,
            size=16,
            numPlates=4,
            numHamburgers=3,
    ):
        self.numPlates = numPlates
        self.numHamburgers = numHamburgers

        self.objs = {}
        self.numThrown = 0

        super().__init__(
            grid_size=size,
            # max_steps=5 * size,
            max_steps=1e10,
            # Set this to True for maximum speed
            see_through_walls=True
        )

    def action_space(self):
        objs = self.objs
        actions = self.actions

    def _gen_grid(self, width, height):
        self.grid = Grid(width, height)

        # Generate the surrounding walls
        self.grid.horz_wall(0, 0)
        self.grid.horz_wall(0, height - 1)
        self.grid.vert_wall(0, 0)
        self.grid.vert_wall(width - 1, 0)

        # return True if not a valid counter space
        def invalid_counter(env, p1):
            return p1[0] + 3 >= env.width or p1[1] <= 2

        def init_conditions():
            assert 'counters' in self.objs.keys(), "No counter"
            assert 'ashcan' in self.objs.keys(), "No ashcan"
            assert 'plates' in self.objs.keys(), "No plates"
            assert 'hamburgers' in self.objs.keys(), "No hamburgers"

            for ashcan in self.objs['ashcan']:
                assert check_abs_state(self, ashcan, 'onfloor'), "Ashcan not on floor"

            for plate in self.objs['plates']:
                on_counter = False
                for counter in self.objs['counters']:
                    on_counter = check_rel_state(self, plate, counter, 'ontop')
                    if on_counter:
                        break
                assert on_counter, "Plate not on counter"

            for hamburger in self.objs['hamburgers']:
                on_plate = False
                for plate in self.objs['plates']:
                    on_plate = check_rel_state(self, hamburger, plate, 'ontop')
                    if on_plate:
                        break
                assert on_plate, "Hamburger not on plate"

        # generate counter
        counters = [Counter('purple', 'counter_0')]
        init_counter = self.place_obj(counters[0], reject_fn=invalid_counter)
        for i in range(1, self.numPlates):
            counter = Counter('purple', 'counter_{}'.format(i))
            x = init_counter[0] + i
            y = init_counter[1]
            self.put_obj(counter, x, y)
            counters.append(counter)
        self.objs['counters'] = counters

        # TODO: generate floor

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
        for plate in random.sample(plates, self.numHamburgers):
            hamburger = S_ball('red', 'hamburger_{}'.format(i))
            self.put_obj(hamburger, *plate.cur_pos)
            hamburgers.append(hamburger)
            i += 1
        self.objs['hamburgers'] = hamburgers

        # generate ashcan on floor
        ashcan = Box('green', 'ashcan_0')
        ashcan.on_floor = True
        self.objs['ashcan'] = [ashcan]
        self.target_pos = self.place_obj(self.objs['ashcan'][0])

        # check init conditions satisfied
        init_conditions()

        # randomize the agent start position and orientation
        self.place_agent()
        self.mission = 'throw the leftovers in the ashcan'

    def step(self, action):
        obs, reward, done, info = super().step(action)
        obj = self.agent_object

        # if dropping an object
        if action == self.actions.drop and obj:
            # if dropped a hamburger into the ashcan
            # pos = [np.all(obj.cur_pos == ashcan.cur_pos) for ashcan in self.objs['ashcan']]
            pos = [check_rel_state(self, obj, ashcan, 'inside') for ashcan in self.objs['ashcan']]
            # if obj in self.objs['hamburgers'] and True in pos:
            if obj in self.objs['hamburgers'] and True in pos:
                # TODO: set reward
                # reward = self._reward()
                self.numThrown += 1
                print('Num remaining hamburgers: ' + str(self.numHamburgers - self.numThrown))

        # done if succesfully throw away all leftovers
        def end_condition():
            for hamburger in self.objs['hamburgers']:
                is_inside = [check_rel_state(self, hamburger, ashcan, 'inside') for ashcan in self.objs['ashcan']]
                if True not in is_inside:
                    return False
            return True

        done = end_condition()

        return obs, reward, done, {}


class ThrowLeftovers16x16N3(ThrowLeftoversEnv):
    def __init__(self):
        super().__init__(size=32, numPlates=4, numHamburgers=3)


register(
    id='MiniGrid-ThrowLeftovers-16x16-N2-v0',
    entry_point='gym_minigrid.envs:ThrowLeftoversEnv'
)    

register(        
    id='MiniGrid-ThrowLeftovers-32x32-N3-v0',
    entry_point='gym_minigrid.envs:ThrowLeftovers32x32N3'
)


