from mini_behavior.floorplan import *
from mini_behavior.register import register



class PreparingSaladFloorplanEnv(FloorPlanEnv):
    """
    Environment in which the agent is instructed to clean a car
    """


    def __init__(
            self,
            mode='cartesian',
            scene_id='rs_int',
            num_objs=None,
            max_steps=1e5,
    ):
        num_objs = {'electric_refrigerator': 1, 'lettuce': 2, 'countertop': 1, 'apple': 2, 'tomato': 2,
                    'radish': 2, 'carving_knife': 1, 'plate': 2, 'cabinet': 1, 'sink': 1}

        self.mission = 'prepare salad'

        super().__init__(mode=mode,
                         scene_id=scene_id,
                         num_objs=num_objs,
                         max_steps=max_steps
                         )

    def _gen_objs(self):
        electric_refrigerator = self.objs['electric_refrigerator'][0]
        lettuce = self.objs['lettuce']
        countertop = self.objs['countertop'][0]
        apple = self.objs['apple']
        tomato = self.objs['tomato']
        radish = self.objs['radish']
        carving_knife = self.objs['carving_knife'][0]
        plate = self.objs['plate']
        cabinet = self.objs['cabinet'][0]
        sink = self.objs['sink'][0]

        self.objs['electric_refrigerator'][0].width = 4 * 2
        self.objs['electric_refrigerator'][0].height = 6 * 2

        self.objs['countertop'][0].width = 6 * 2
        self.objs['countertop'][0].height = 4 * 2

        self.objs['sink'][0].width = 4 * 2
        self.objs['sink'][0].height = 4 * 2

        self.place_obj(countertop)
        self.place_obj(electric_refrigerator)
        self.place_obj(cabinet)
        self.place_obj(sink)

        countertop_pos = self._rand_subset(countertop.all_pos, 6)
        self.put_obj(lettuce[0], *countertop_pos[0], 1)
        self.put_obj(lettuce[1], *countertop_pos[1], 1)
        self.put_obj(apple[0], *countertop_pos[2], 1)
        self.put_obj(apple[1], *countertop_pos[3], 1)

        fridge_pos = self._rand_subset(electric_refrigerator.all_pos, 2)
        self.put_obj(tomato[0], *fridge_pos[0], 0)
        self.put_obj(tomato[1], *fridge_pos[1], 2)

        self.put_obj(radish[0], *countertop_pos[4], 1)
        self.put_obj(radish[1], *countertop_pos[5], 1)

        cabinet_pos = self._rand_subset(cabinet.all_pos, 3)
        self.put_obj(plate[0], *cabinet_pos[0], 1)
        plate[0].states['dustyable'].set_value(False)
        self.put_obj(plate[1], *cabinet_pos[1], 2)
        plate[1].states['dustyable'].set_value(False)
        self.put_obj(carving_knife, *cabinet_pos[2], 0)



    def _end_conditions(self):
        lettuces = self.objs['lettuce']
        apples = self.objs['apple']
        tomatos = self.objs['tomato']
        radishes = self.objs['radish']
        plates = self.objs['plate']

        def forpair(vegs):
            for veg in vegs:
                forpair = False
                for plate in plates:
                    if veg.check_rel_state(self, plate, 'onTop'):
                        forpair = True
                        break
                if not forpair:
                    return False

            for plate in plates:
                forpair = False
                for veg in vegs:
                    if veg.check_rel_state(self, plate, 'onTop'):
                        forpair = True
                        break
                if not forpair:
                    return False

        def forpair_slice(vegs):
            for veg in vegs:
                forpair = False
                for plate in plates:
                    if plate.check_abs_state(self, 'sliced') and veg.check_rel_state(self, plate, 'onTop'):
                        forpair = True
                        break
                if not forpair:
                    return False

            for plate in plates:
                forpair = False
                for veg in vegs:
                    if veg.check_abs_state(self, 'sliced') and veg.check_rel_state(self, plate, 'onTop'):
                        forpair = True
                        break
                if not forpair:
                    return False

            return True

        if not forpair(lettuces) or not forpair_slice(apples) or not forpair_slice(tomatos) or not forpair(radishes):
            return False

        return True


# non human input env
register(
    id='MiniGrid-PreparingSaladFloorplan-16x16-N2-v0',
    entry_point='mini_behavior.envs:PreparingSaladFloorplanEnv'
)

# human input env
register(
    id='MiniGrid-PreparingSaladFloorplan-16x16-N2-v1',
    entry_point='mini_behavior.envs:PreparingSaladFloorplanEnv',
    kwargs={'mode': 'cartesian'}
)
