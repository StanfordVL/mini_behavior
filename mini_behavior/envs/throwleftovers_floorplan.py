from mini_behavior.floorplan import *
from mini_behavior.register import register
import os


class ThrowLeftoversSceneEnv(FloorPlanEnv):
    """
    Environment in which the agent is instructed to throw away all leftovers into a trash can.
    """

    def __init__(
            self,
            mode='cartesian',
            scene_id='rs_int',
            num_objs=None,
            max_steps=1e5,
    ):
        if num_objs is None:
            num_objs = {'countertop': 1,
                        'plate': 4,
                        'hamburger': 3,
                        'ashcan': 1}

        self.mission = 'throw all {} leftovers in the ashcan'.format(num_objs['hamburger'])

        super().__init__(mode=mode,
                         scene_id=scene_id,
                         num_objs=num_objs,
                         max_steps=max_steps
                         )

    def _gen_objs(self):
        # # generate counter
        # place all objects
        countertop = self.objs['countertop'][0]
        plates = self.objs['plate']
        hamburgers = self.objs['hamburger']
        ashcan = self.objs['ashcan'][0]

        # place countertop
        self.place_obj(countertop)

        # place plates
        i = 0
        for pos in self._rand_subset(countertop.all_pos, len(plates)):
            self.put_obj(plates[i], *pos, 1)
            i += 1

        # place hamburgers
        i = 0
        for plate in self._rand_subset(plates, len(hamburgers)):
            self.put_obj(hamburgers[i], *plate.cur_pos, 2)
            i += 1

        # generate ashcan on floor
        self.target_pos = self.place_obj(ashcan)

    def _init_conditions(self):
        assert 'countertop' in self.objs.keys(), "No counter"
        assert 'ashcan' in self.objs.keys(), "No ashcan"
        assert 'plate' in self.objs.keys(), "No plates"
        assert 'hamburger' in self.objs.keys(), "No hamburgers"

        countertop = self.objs['countertop'][0]
        plates = self.objs['plate']
        hamburgers = self.objs['hamburger']
        ashcan = self.objs['ashcan'][0]

        assert ashcan.check_abs_state(self, 'onfloor'), "Ashcan not on floor"

        for plate in plates:
            on_counter = plate.check_rel_state(self, countertop, 'onTop')
            assert on_counter, "Plate not on counter"

        for hamburger in hamburgers:
            on_plate = False
            for plate in plates:
                on_plate = hamburger.check_rel_state(self, plate, 'onTop')
                if on_plate:
                    break
            assert on_plate, "Hamburger not on plate"

        return True

    def _reward(self):
        # fraction of hamburgers thrown away
        num_thrown = 0
        for hamburger in self.objs['hamburger']:
            is_inside = [hamburger.check_rel_state(self, ashcan, 'inside') for ashcan in self.objs['ashcan']]
            if True in is_inside:
                num_thrown += 1

        return num_thrown / len(self.objs['hamburger'])

    def _end_conditions(self):
        for hamburger in self.objs['hamburger']:
            is_inside = [hamburger.check_rel_state(self, ashcan, 'inside') for ashcan in self.objs['ashcan']]
            if True not in is_inside:
                return False
        return True


register(
    id='MiniGrid-ThrowLeftoversSceneEnv-0x0-N2-v0',
    entry_point='mini_behavior.envs:ThrowLeftoversSceneEnv',
    kwargs={}
)
